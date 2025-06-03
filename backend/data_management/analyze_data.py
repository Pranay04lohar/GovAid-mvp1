import sqlite3
import json
import os
import logging
from typing import Dict, List, Set
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataAnalyzer:
    def __init__(self, db_path: str = None):
        """Initialize the analyzer with database connection."""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "yojnabuddy.db")
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_all_urls(self) -> Set[str]:
        """Get all URLs from the JSON files."""
        urls = set()
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        
        for json_file in os.listdir(output_dir):
            if json_file.endswith('_urls.json'):
                with open(os.path.join(output_dir, json_file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        urls.update(data)
                    elif isinstance(data, dict) and 'urls' in data:
                        urls.update(data['urls'])
        
        return urls

    def get_db_urls(self) -> Set[str]:
        """Get all URLs from the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT url FROM schemes")
        return {row['url'] for row in cursor.fetchall()}

    def analyze_missing_data(self):
        """Analyze missing data and print statistics."""
        all_urls = self.get_all_urls()
        db_urls = self.get_db_urls()
        
        missing_urls = all_urls - db_urls
        extra_urls = db_urls - all_urls
        
        logger.info(f"Total URLs in JSON files: {len(all_urls)}")
        logger.info(f"Total URLs in database: {len(db_urls)}")
        logger.info(f"Missing URLs (not in DB): {len(missing_urls)}")
        logger.info(f"Extra URLs (in DB but not in JSON): {len(extra_urls)}")
        
        if missing_urls:
            logger.info("\nMissing URLs:")
            for url in sorted(missing_urls):
                logger.info(f"- {url}")
        
        if extra_urls:
            logger.info("\nExtra URLs:")
            for url in sorted(extra_urls):
                logger.info(f"- {url}")

    def export_category_data(self, output_dir: str = None):
        """Export data organized by categories."""
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'category_data')
        os.makedirs(output_dir, exist_ok=True)
        
        cursor = self.conn.cursor()
        
        # Get all categories
        cursor.execute("SELECT DISTINCT category FROM categories ORDER BY category")
        categories = [row['category'] for row in cursor.fetchall()]
        
        # Export data for each category
        for category in categories:
            logger.info(f"Exporting data for category: {category}")
            
            # Get all schemes for this category
            cursor.execute("""
            SELECT DISTINCT s.*, 
                   GROUP_CONCAT(DISTINCT c.category) as categories,
                   GROUP_CONCAT(DISTINCT b.benefit) as benefits,
                   GROUP_CONCAT(DISTINCT e.criterion) as eligibility_criteria,
                   GROUP_CONCAT(DISTINCT d.document) as required_documents
            FROM schemes s
            LEFT JOIN categories c ON s.id = c.scheme_id
            LEFT JOIN benefits b ON s.id = b.scheme_id
            LEFT JOIN eligibility_criteria e ON s.id = e.scheme_id
            LEFT JOIN required_documents d ON s.id = d.scheme_id
            WHERE c.category = ?
            GROUP BY s.id
            """, (category,))
            
            schemes = []
            for row in cursor.fetchall():
                scheme = dict(row)
                
                # Convert comma-separated strings to lists
                for field in ['categories', 'benefits', 'eligibility_criteria', 'required_documents']:
                    if scheme[field]:
                        scheme[field] = scheme[field].split(',')
                    else:
                        scheme[field] = []
                
                # Get FAQs
                cursor.execute("SELECT question, answer FROM faqs WHERE scheme_id = ?", (row['id'],))
                scheme['faqs'] = [dict(faq) for faq in cursor.fetchall()]
                
                schemes.append(scheme)
            
            # Save to JSON file
            output_file = os.path.join(output_dir, f"{category}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(schemes, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(schemes)} schemes to {output_file}")

    def __del__(self):
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    analyzer = DataAnalyzer()
    
    # Analyze missing data
    logger.info("Analyzing missing data...")
    analyzer.analyze_missing_data()
    
    # Export category data
    logger.info("\nExporting category data...")
    analyzer.export_category_data()

if __name__ == "__main__":
    main() 