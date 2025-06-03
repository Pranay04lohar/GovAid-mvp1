import logging
import asyncio
from playwright.async_api import async_playwright
from scraper import SchemeScraper
from database import Database
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def get_first_scheme_url() -> str:
    """Get the first available scheme URL from the search page using Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Navigate to the search page
            await page.goto("https://www.myscheme.gov.in/search")
            
            # Wait for the page to be fully loaded
            await page.wait_for_load_state('networkidle')
            
            # Add a small delay to ensure dynamic content is loaded
            await asyncio.sleep(2)
            
            # Try multiple selectors for scheme links
            selectors = [
                'a[href^="/schemes/"]',
                'a[href*="schemes"]',
                '.scheme-link',  # Add any other potential selectors
            ]
            
            for selector in selectors:
                try:
                    # Wait for the selector with a shorter timeout
                    await page.wait_for_selector(selector, timeout=5000)
                    scheme_link = await page.query_selector(selector)
                    if scheme_link:
                        href = await scheme_link.get_attribute('href')
                        if href and '/schemes/' in href:
                            return "https://www.myscheme.gov.in" + href
                except Exception as e:
                    logger.debug(f"Selector {selector} not found: {str(e)}")
                    continue
            
            # If no links found, try to get the page content for debugging
            content = await page.content()
            logger.error(f"No scheme links found. Page content length: {len(content)}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting scheme URL: {str(e)}")
            return None
        finally:
            await browser.close()

async def test_single_scheme():
    # Initialize scraper and database
    scraper = SchemeScraper()
    db = Database()
    
    # Get a working scheme URL
    test_url = await get_first_scheme_url()
    if not test_url:
        logger.error("Failed to get a working scheme URL")
        return
    
    logger.info(f"Testing scraper with URL: {test_url}")
    
    # Add a small delay before scraping to avoid rate limiting
    await asyncio.sleep(1)
    
    # Scrape the scheme
    scheme_data = scraper.extract_scheme_details(test_url)
    
    if not scheme_data:
        logger.error("Failed to scrape scheme data")
        return
    
    logger.info("Successfully scraped scheme data")
    logger.info(f"Scheme name: {scheme_data['name']}")
    logger.info(f"State: {scheme_data['state']}")
    logger.info(f"Number of categories: {len(scheme_data['categories'])}")
    logger.info(f"Number of benefits: {len(scheme_data['benefits'])}")
    logger.info(f"Number of FAQs: {len(scheme_data['faqs'])}")
    
    # Verify data in database
    saved_scheme = db.get_scheme_by_url(test_url)
    
    if saved_scheme:
        logger.info("\nVerifying saved data in database:")
        logger.info(f"Name matches: {saved_scheme['name'] == scheme_data['name']}")
        logger.info(f"State matches: {saved_scheme['state'] == scheme_data['state']}")
        logger.info(f"Categories count matches: {len(saved_scheme['categories']) == len(scheme_data['categories'])}")
        logger.info(f"Benefits count matches: {len(saved_scheme['benefits']) == len(scheme_data['benefits'])}")
        logger.info(f"FAQs count matches: {len(saved_scheme['faqs']) == len(scheme_data['faqs'])}")
        
        # Print some sample data
        logger.info("\nSample data from database:")
        logger.info(f"Categories: {saved_scheme['categories'][:3]}")
        logger.info(f"First benefit: {saved_scheme['benefits'][0] if saved_scheme['benefits'] else 'None'}")
        logger.info(f"First FAQ: {saved_scheme['faqs'][0] if saved_scheme['faqs'] else 'None'}")
    else:
        logger.error("Failed to retrieve scheme from database")

if __name__ == "__main__":
    asyncio.run(test_single_scheme()) 