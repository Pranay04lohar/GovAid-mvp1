import requests
from bs4 import BeautifulSoup
import json
import time
from tqdm import tqdm
import logging
from typing import Dict, List, Optional, Tuple
import re
from data_management.database import Database
import asyncio
from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SchemeScraper:
    BASE_URL = "https://www.myscheme.gov.in"
    SEARCH_URL = f"{BASE_URL}/search"
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.db = Database()
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage."""
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def extract_text_safely(self, element, selector: str, default: str = "") -> str:
        """Safely extract text from an element using a selector."""
        try:
            found = element.select_one(selector)
            if found:
                # Clean up the text
                text = found.text.strip()
                # Remove extra whitespace and newlines
                text = ' '.join(text.split())
                # Skip if it's a navigation element
                if text.lower() in ['quick links', 'home', 'search', 'about']:
                    return default
                return text
            return default
        except Exception:
            return default

    def extract_list_items(self, element, selector: str) -> List[str]:
        """Extract list items from an element using a selector."""
        try:
            items = element.select(selector)
            return [item.text.strip() for item in items if item.text.strip()]
        except Exception:
            return []

    def format_table_data(self, text: str) -> List[str]:
        """Format table-like data into readable lines."""
        lines = []
        # Split by common table separators
        rows = text.split('\n')
        current_row = []
        
        for row in rows:
            # Clean up the row
            row = row.strip()
            if not row:
                continue
            
            # Check if this is a header row (contains words like "No.", "Class", "Course", etc.)
            is_header = any(word in row.lower() for word in ['no.', 'class', 'course', 'fee', 'assistance'])
            
            # Split by common table delimiters
            cells = [cell.strip() for cell in row.split('|') if cell.strip()]
            if not cells:
                # Try splitting by tabs or multiple spaces
                cells = [cell.strip() for cell in row.split('\t') if cell.strip()]
                if not cells:
                    # Try splitting by common delimiters
                    for delimiter in ['₹', '/-', 'Class', 'Course']:
                        if delimiter in row:
                            parts = row.split(delimiter)
                            cells = [part.strip() for part in parts if part.strip()]
                            if cells:
                                # Add the delimiter back to the appropriate parts
                                cells = [f"{cell}{delimiter}" if i < len(cells)-1 else cell 
                                       for i, cell in enumerate(cells)]
                                break
            
            if cells:
                if is_header:
                    # Add a separator line after headers
                    if current_row:
                        lines.append(' | '.join(current_row))
                        lines.append('-' * 80)  # Add a separator
                    current_row = cells
                else:
                    # Format as a readable line
                    formatted_line = ' | '.join(cells)
                    lines.append(formatted_line)
        
        # Add the last row if exists
        if current_row:
            lines.append(' | '.join(current_row))
        
        return lines

    def extract_section_content(self, soup: BeautifulSoup, section_title: str) -> List[str]:
        """Extract content from a section between two h3 headings."""
        content = []
        section = soup.find('h3', string=section_title)
        if section:
            current = section.find_next()
            while current and current.name != 'h3':
                if current.name == 'div' and 'markdown-options' in current.get('class', []):
                    text = current.text.strip()
                    # Improved: Always split by lines, and format tables if detected
                    if '|' in text or '\t' in text or text.count('\n') > 3:
                        content.extend(self.format_table_data(text))
                    else:
                        # Split content into lines and clean each line
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        content.extend(lines)
                current = current.find_next()
        return content

    def extract_faqs(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract FAQs from the page."""
        faqs = []
        try:
            faq_section = soup.find('h3', string='Frequently Asked Questions')
            if faq_section:
                current = faq_section.find_next()
                while current and current.name != 'h3':
                    if current.name == 'div' and 'cursor-pointer' in current.get('class', []):
                        question = current.text.strip()
                        answer_div = current.find_next('div', class_='rounded-b')
                        if answer_div:
                            answer = answer_div.find('div', class_='markdown-options')
                            answer_text = answer.text.strip() if answer else ""
                            if question and answer_text:
                                faqs.append({
                                    'question': question,
                                    'answer': answer_text
                                })
                    current = current.find_next()
        except Exception as e:
            logger.error(f"Error extracting FAQs: {str(e)}")
        return faqs

    def extract_state(self, soup: BeautifulSoup, name: str) -> str:
        """Extract the state from the <h3> tag with class 'text-raven', or fallback to name-based extraction."""
        state_tag = soup.find('h3', class_='text-raven')
        if state_tag and state_tag.text.strip():
            return state_tag.text.strip()
        return self.extract_state_from_name(name)

    def extract_state_from_name(self, name: str) -> str:
        """Extract state from the scheme name."""
        try:
            if not name:
                return "All India"
            
            # Remove any extra whitespace
            name = name.strip()
            
            # Check if the name contains a dash
            if '-' in name:
                # Split by dash and get the last part
                parts = name.split('-')
                state_candidate = parts[-1].strip()
                
                # Basic validation
                if len(state_candidate) > 2:
                    # Remove any common prefixes/suffixes
                    state_candidate = state_candidate.replace('Scheme', '').strip()
                    return state_candidate
            
            # If no state found in name, check if it's a state-specific scheme
            if 'tamil nadu' in name.lower():
                return 'Tamil Nadu'
            elif 'karnataka' in name.lower():
                return 'Karnataka'
            # Add more state checks as needed
            
            return "All India"
        except Exception as e:
            logger.error(f"Error extracting state from name '{name}': {str(e)}")
            return "All India"

    def extract_scheme_details(self, scheme_url: str) -> Dict:
        """Extract details from an individual scheme page."""
        soup = self.get_page(scheme_url)
        if not soup:
            return {}

        try:
            # Basic scheme information
            name = None
            # Try the specific h1 selector first
            name_tag = soup.find('h1', class_='font-bold text-xl sm:text-2xl text-[#24262B] dark:text-white mt-1')
            if name_tag:
                name = name_tag.text.strip()
                logger.info(f"Extracted name '{name}' from h1 tag.")
            
            # If no name found, try other selectors as fallback
            if not name:
                name_selectors = [
                    '.scheme-title',
                    '.title',
                    'h2',
                    '[class*="scheme-name"]',
                    '[class*="title"]'
                ]
                
                for selector in name_selectors:
                    name = self.extract_text_safely(soup, selector)
                    if name and name.lower() not in ['quick links', 'home', 'search', 'about']:
                        # Clean up the name
                        name = name.replace('Scheme', '').strip()
                        # Remove any state prefixes
                        name = re.sub(r'^[A-Za-z\s]+-', '', name)
                        break
            
            # If still no name, try to extract from FAQ question
            if not name:
                faq_section = soup.find('h3', string='Frequently Asked Questions')
                if faq_section:
                    first_faq = faq_section.find_next('div', class_='cursor-pointer')
                    if first_faq:
                        question = first_faq.text.strip()
                        # Extract scheme name from FAQ question
                        match = re.search(r'What is the "(.*?)" scheme', question)
                        if match:
                            name = match.group(1)
                            logger.info(f"Extracted name '{name}' from FAQ question.")
            
            # If still no name, try to extract from URL and clean it up
            if not name:
                name = scheme_url.split('/')[-1]
                # Remove common suffixes and clean up
                name = name.replace('-scheme', '').replace('-', ' ')
                # Convert to title case and clean up
                name = ' '.join(word.capitalize() for word in name.split())
                # Try to make it more readable
                name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)  # Add space between camelCase
                logger.info(f"Extracted name '{name}' from URL.")
            
            description = self.extract_text_safely(soup, 'div.markdown-options')
            
            # Categories (from tags)
            categories = []
            # Try multiple selectors for categories
            category_selectors = [
                'div.grid div.bg-transparent',  # Primary selector
                '.category-tag',
                '.tag',
                '[class*="category"]',
                '[class*="tag"]'
            ]
            
            for selector in category_selectors:
                category_tags = soup.select(selector)
                if category_tags:
                    categories = [tag.text.strip() for tag in category_tags if tag.text.strip()]
                    if categories:
                        # Remove duplicates and sort
                        categories = sorted(list(set(categories)))
                        # Clean up category names
                        categories = [cat.replace('Category:', '').strip() for cat in categories]
                        # Limit to first 3 unique categories for MVP
                        #categories = categories[:3]
                        break
            
            # Extract content from each section
            eligibility_criteria = self.extract_section_content(soup, 'Eligibility')
            benefits = self.extract_section_content(soup, 'Benefits')
            application_process = self.extract_section_content(soup, 'Application Process')
            required_documents = self.extract_section_content(soup, 'Documents Required')
            
            # FAQs
            faqs = self.extract_faqs(soup)
            
            # Extract state from <h3> tag or fallback
            state = self.extract_state(soup, name)
            logger.info(f"Extracted state '{state}' from page.")
            
            scheme_data = {
                'name': name,
                'description': description,
                'categories': categories,
                'eligibility_criteria': eligibility_criteria,
                'benefits': benefits,
                'application_process': application_process,
                'required_documents': required_documents,
                'faqs': faqs,
                'url': scheme_url,
                'state': state
            }
            
            # Save to database
            self.db.save_scheme(scheme_data)
            
            return scheme_data
            
        except Exception as e:
            logger.error(f"Error extracting scheme details from {scheme_url}: {str(e)}")
            return {}

    def scrape_schemes(self) -> List[Dict]:
        """Main method to scrape all schemes."""
        schemes = []
        page = 1
        
        while True:
            url = f"{self.SEARCH_URL}?page={page}"
            soup = self.get_page(url)
            
            if not soup:
                break
                
            # Find all scheme links on the page
            scheme_links = soup.select('a[href^="/schemes/"]')
            
            if not scheme_links:
                break
                
            for link in tqdm(scheme_links, desc=f"Processing page {page}"):
                scheme_url = self.BASE_URL + link['href']
                scheme_details = self.extract_scheme_details(scheme_url)
                
                if scheme_details:
                    schemes.append(scheme_details)
                
                # Be nice to the server
                time.sleep(1)
            
            page += 1
            
        return schemes

    def get_scheme_urls(self, category_url: str, num_schemes: int) -> List[str]:
        """Get scheme URLs for a specific category."""
        urls = []
        page = 1
        
        while len(urls) < num_schemes:
            # Construct the URL with pagination
            page_url = f"{category_url}?page={page}"
            logger.info(f"Fetching page {page} for {category_url}")
            
            soup = self.get_page(page_url)
            if not soup:
                break
            
            # Find all scheme links - try multiple selectors
            scheme_links = []
            selectors = [
                'a[href*="/scheme/"]',
                'a[href*="/schemes/"]',
                '.scheme-card a',
                '.scheme-link',
                'a.scheme-link',
                'div[class*="scheme"] a',
                'a[href*="myscheme.gov.in/scheme"]'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    scheme_links = links
                    logger.info(f"Found links using selector: {selector}")
                    break
            
            if not scheme_links:
                # If no links found, try to find any links that might be scheme links
                all_links = soup.find_all('a')
                for link in all_links:
                    href = link.get('href', '')
                    if href and ('scheme' in href.lower() or 'schemes' in href.lower()):
                        scheme_links.append(link)
            
            if not scheme_links:
                logger.warning(f"No scheme links found on page {page}")
                break
            
            # Extract URLs
            for link in scheme_links:
                href = link.get('href')
                if href:
                    # Handle relative URLs
                    if href.startswith('/'):
                        full_url = f"{self.BASE_URL}{href}"
                    elif not href.startswith('http'):
                        full_url = f"{self.BASE_URL}/{href}"
                    else:
                        full_url = href
                    
                    # Only add URLs that look like scheme pages
                    if ('scheme' in full_url.lower() or 'schemes' in full_url.lower()) and full_url not in urls:
                        urls.append(full_url)
                        if len(urls) >= num_schemes:
                            break
            
            page += 1
            time.sleep(1)  # Be nice to the server
        
        logger.info(f"Found {len(urls)} URLs for category {category_url}")
        return urls

async def get_all_scheme_urls():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.myscheme.gov.in/search")
        await page.wait_for_selector('a[href^=\"/schemes/\"]', timeout=10000)
        links = await page.query_selector_all('a[href^=\"/schemes/\"]')
        urls = []
        for link in links:
            href = await link.get_attribute('href')
            if href:
                urls.append("https://www.myscheme.gov.in" + href)
        await browser.close()
        return urls

def main():
    scraper = SchemeScraper()
    logger.info("Starting scheme scraping with Playwright...")

    # Get all scheme URLs using Playwright
    scheme_urls = asyncio.run(get_all_scheme_urls())
    logger.info(f"Found {len(scheme_urls)} scheme URLs.")

    count = 0
    for url in scheme_urls:
        scheme_data = scraper.extract_scheme_details(url)
        if scheme_data:
            count += 1

    logger.info(f"Scraped {count} schemes successfully!")
    logger.info("Scraping completed!")

if __name__ == "__main__":
    main() 