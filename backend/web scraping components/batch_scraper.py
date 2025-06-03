import json
import os
import logging
from typing import List, Dict
from tqdm import tqdm
from web_scraping_components.scraper import SchemeScraper
from data_management.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_urls_from_json(json_file: str) -> List[str]:
    """Load URLs from a JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle both array of URLs and object with 'urls' key
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'urls' in data:
                return data['urls']
            else:
                logger.error(f"Invalid JSON format in {json_file}")
                return []
    except Exception as e:
        logger.error(f"Error loading URLs from {json_file}: {str(e)}")
        return []

def process_all_categories():
    """Process all scheme URLs from category JSON files."""
    # Initialize scraper and database
    scraper = SchemeScraper()
    db = Database()
    
    # Get all JSON files from the output directory
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    json_files = [f for f in os.listdir(output_dir) if f.endswith('_urls.json')]
    
    total_processed = 0
    total_success = 0
    total_failed = 0
    
    # Process each category file
    for json_file in json_files:
        category = json_file.replace('_urls.json', '')
        logger.info(f"Processing category: {category}")
        
        # Load URLs for this category
        urls = load_urls_from_json(os.path.join(output_dir, json_file))
        logger.info(f"Found {len(urls)} URLs for category {category}")
        
        # Process each URL
        for url in tqdm(urls, desc=f"Processing {category}"):
            try:
                # Extract scheme details
                scheme_data = scraper.extract_scheme_details(url)
                if scheme_data:
                    # Add category to scheme data
                    scheme_data['categories'] = [category]
                    
                    # Save to database
                    scheme_id = db.save_scheme(scheme_data)
                    if scheme_id:
                        total_success += 1
                    else:
                        total_failed += 1
                else:
                    total_failed += 1
                
                total_processed += 1
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {str(e)}")
                total_failed += 1
                total_processed += 1
                continue
    
    # Print summary
    logger.info("\nScraping Summary:")
    logger.info(f"Total URLs processed: {total_processed}")
    logger.info(f"Successfully scraped: {total_success}")
    logger.info(f"Failed to scrape: {total_failed}")

if __name__ == "__main__":
    process_all_categories() 