import json
import logging
from scraper import SchemeScraper
from bs4 import BeautifulSoup
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def inspect_html_structure(soup: BeautifulSoup):
    """Inspect the HTML structure of the page."""
    logger.info("\n=== HTML Structure Inspection ===")
    
    # Inspect the h1 heading specifically for state information
    h1 = soup.find('h1')
    if h1:
        logger.info("\nH1 Heading Content:")
        logger.info(f"Raw text: {h1.text.strip()}")
        if '-' in h1.text:
            parts = h1.text.split('-')
            logger.info(f"Parts after splitting by '-': {[p.strip() for p in parts]}")
    
    # Inspect Categories
    logger.info("\n1. Categories Section:")
    category_div = soup.find('div', class_='grid')
    if category_div:
        logger.info("Found category div with classes:", category_div.get('class', []))
        for tag in category_div.find_all('div', class_='bg-transparent'):
            logger.info(f"Category tag: {tag.text.strip()}")
    
    # Inspect Benefits
    logger.info("\n2. Benefits Section:")
    benefits_section = soup.find('h3', string='Benefits')
    if benefits_section:
        logger.info("Found Benefits section")
        current = benefits_section.find_next()
        while current and current.name != 'h3':
            if current.name == 'div':
                logger.info(f"Div class: {current.get('class', [])}")
                logger.info(f"Content: {current.text.strip()[:100]}...")
            current = current.find_next()
    
    # Inspect Application Process
    logger.info("\n3. Application Process Section:")
    process_section = soup.find('h3', string='Application Process')
    if process_section:
        logger.info("Found Application Process section")
        current = process_section.find_next()
        while current and current.name != 'h3':
            if current.name == 'div':
                logger.info(f"Div class: {current.get('class', [])}")
                logger.info(f"Content: {current.text.strip()[:100]}...")
            current = current.find_next()
    
    # Inspect Required Documents
    logger.info("\n4. Required Documents Section:")
    docs_section = soup.find('h3', string='Documents Required')
    if docs_section:
        logger.info("Found Documents Required section")
        current = docs_section.find_next()
        while current and current.name != 'h3':
            if current.name == 'div':
                logger.info(f"Div class: {current.get('class', [])}")
                logger.info(f"Content: {current.text.strip()[:100]}...")
            current = current.find_next()
    
    # Inspect FAQs
    logger.info("\n5. FAQs Section:")
    faq_section = soup.find('h3', string='Frequently Asked Questions')
    if faq_section:
        logger.info("Found FAQs section")
        current = faq_section.find_next()
        while current and current.name != 'h3':
            if current.name == 'div':
                logger.info(f"Div class: {current.get('class', [])}")
                logger.info(f"Content: {current.text.strip()[:100]}...")
            current = current.find_next()

def test_single_scheme():
    """Test the scraper with a single scheme URL."""
    try:
        scraper = SchemeScraper()
        
        # Test URL - Government Service Home scheme
        test_url = "https://www.myscheme.gov.in/schemes/gshtn"
        
        logger.info(f"Testing scraper with URL: {test_url}")
        logger.info("-" * 80)
        
        # Get the page content
        soup = scraper.get_page(test_url)
        if not soup:
            logger.error("Failed to fetch the page")
            return
            
        # Inspect HTML structure
        inspect_html_structure(soup)
        
        # Get the scheme details
        scheme_details = scraper.extract_scheme_details(test_url)
        
        if not scheme_details:
            logger.error("No scheme details were extracted!")
            return
        
        # Print each field with clear separation
        logger.info("\n=== Extracted Data ===")
        logger.info("\n1. Scheme Name:")
        logger.info(scheme_details.get('name', 'Not found'))
        
        logger.info("\n2. Description:")
        logger.info(scheme_details.get('description', 'Not found'))
        
        logger.info("\n3. Categories:")
        for category in scheme_details.get('categories', []):
            logger.info(f"- {category}")
        
        logger.info("\n4. Eligibility Criteria:")
        for criterion in scheme_details.get('eligibility_criteria', []):
            logger.info(f"- {criterion}")
        
        logger.info("\n5. Benefits:")
        for benefit in scheme_details.get('benefits', []):
            logger.info(f"- {benefit}")
        
        logger.info("\n6. Application Process:")
        for step in scheme_details.get('application_process', []):
            logger.info(f"- {step}")
        
        logger.info("\n7. Required Documents:")
        for doc in scheme_details.get('required_documents', []):
            logger.info(f"- {doc}")
        
        logger.info("\n8. FAQs:")
        for faq in scheme_details.get('faqs', []):
            logger.info(f"\nQ: {faq['question']}")
            logger.info(f"A: {faq['answer']}")
        
        logger.info("\n9. URL:")
        logger.info(scheme_details.get('url', 'Not found'))
        
        logger.info("\n10. State:")
        logger.info(scheme_details.get('state', 'Not found'))
        
        # Save the extracted data to a file for inspection
        with open('test_scheme.json', 'w', encoding='utf-8') as f:
            json.dump(scheme_details, f, ensure_ascii=False, indent=2)
        logger.info("\nFull extracted data saved to test_scheme.json")
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_single_scheme() 