import sqlite3
import logging
import json
from typing import List, Dict
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self, db_path: str = None):
        """Initialize the validator with database connection."""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "yojnabuddy.db")
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def check_missing_fields(self) -> Dict:
        """Check for schemes with missing required fields."""
        cursor = self.conn.cursor()
        results = {
            'missing_name': [],
            'missing_description': [],
            'missing_state': [],
            'missing_url': []
        }
        
        # Check for missing required fields
        cursor.execute('''
        SELECT id, name, description, state, url 
        FROM schemes 
        WHERE name IS NULL OR name = ''
           OR description IS NULL OR description = ''
           OR state IS NULL OR state = ''
           OR url IS NULL OR url = ''
        ''')
        
        for row in cursor.fetchall():
            if not row['name']:
                results['missing_name'].append(row['id'])
            if not row['description']:
                results['missing_description'].append(row['id'])
            if not row['state']:
                results['missing_state'].append(row['id'])
            if not row['url']:
                results['missing_url'].append(row['id'])
        
        return results

    def check_duplicates(self) -> List[Dict]:
        """Check for duplicate schemes based on name and URL."""
        cursor = self.conn.cursor()
        duplicates = []
        
        # Check for duplicate names
        cursor.execute('''
        SELECT name, COUNT(*) as count, GROUP_CONCAT(id) as ids
        FROM schemes
        GROUP BY name
        HAVING count > 1
        ''')
        
        for row in cursor.fetchall():
            duplicates.append({
                'type': 'name',
                'value': row['name'],
                'count': row['count'],
                'ids': row['ids'].split(',')
            })
        
        # Check for duplicate URLs
        cursor.execute('''
        SELECT url, COUNT(*) as count, GROUP_CONCAT(id) as ids
        FROM schemes
        GROUP BY url
        HAVING count > 1
        ''')
        
        for row in cursor.fetchall():
            duplicates.append({
                'type': 'url',
                'value': row['url'],
                'count': row['count'],
                'ids': row['ids'].split(',')
            })
        
        return duplicates

    def check_related_data(self) -> Dict:
        """Check for schemes missing related data."""
        cursor = self.conn.cursor()
        results = {
            'missing_categories': [],
            'missing_benefits': [],
            'missing_eligibility': [],
            'missing_documents': [],
            'missing_faqs': []
        }
        
        # Get all scheme IDs
        cursor.execute('SELECT id FROM schemes')
        scheme_ids = [row['id'] for row in cursor.fetchall()]
        
        for scheme_id in scheme_ids:
            # Check categories
            cursor.execute('SELECT COUNT(*) as count FROM categories WHERE scheme_id = ?', (scheme_id,))
            if cursor.fetchone()['count'] == 0:
                results['missing_categories'].append(scheme_id)
            
            # Check benefits
            cursor.execute('SELECT COUNT(*) as count FROM benefits WHERE scheme_id = ?', (scheme_id,))
            if cursor.fetchone()['count'] == 0:
                results['missing_benefits'].append(scheme_id)
            
            # Check eligibility criteria
            cursor.execute('SELECT COUNT(*) as count FROM eligibility_criteria WHERE scheme_id = ?', (scheme_id,))
            if cursor.fetchone()['count'] == 0:
                results['missing_eligibility'].append(scheme_id)
            
            # Check required documents
            cursor.execute('SELECT COUNT(*) as count FROM required_documents WHERE scheme_id = ?', (scheme_id,))
            if cursor.fetchone()['count'] == 0:
                results['missing_documents'].append(scheme_id)
            
            # Check FAQs
            cursor.execute('SELECT COUNT(*) as count FROM faqs WHERE scheme_id = ?', (scheme_id,))
            if cursor.fetchone()['count'] == 0:
                results['missing_faqs'].append(scheme_id)
        
        return results

    def export_to_json(self, output_dir: str = None):
        """Export the database to JSON files for manual review."""
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data_export')
        os.makedirs(output_dir, exist_ok=True)
        
        cursor = self.conn.cursor()
        
        # Get all schemes
        cursor.execute('''
        SELECT s.*, 
               GROUP_CONCAT(DISTINCT c.category) as categories,
               GROUP_CONCAT(DISTINCT b.benefit) as benefits,
               GROUP_CONCAT(DISTINCT e.criterion) as eligibility_criteria,
               GROUP_CONCAT(DISTINCT d.document) as required_documents
        FROM schemes s
        LEFT JOIN categories c ON s.id = c.scheme_id
        LEFT JOIN benefits b ON s.id = b.scheme_id
        LEFT JOIN eligibility_criteria e ON s.id = e.scheme_id
        LEFT JOIN required_documents d ON s.id = d.scheme_id
        GROUP BY s.id
        ''')
        
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
            cursor.execute('SELECT question, answer FROM faqs WHERE scheme_id = ?', (row['id'],))
            scheme['faqs'] = [dict(faq) for faq in cursor.fetchall()]
            
            schemes.append(scheme)
        
        # Save to JSON file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'schemes_{timestamp}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(schemes, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(schemes)} schemes to {output_file}")

    def __del__(self):
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    validator = DataValidator()
    
    # Check for missing fields
    logger.info("Checking for missing fields...")
    missing_fields = validator.check_missing_fields()
    for field, ids in missing_fields.items():
        if ids:
            logger.warning(f"Found {len(ids)} schemes with missing {field}")
    
    # Check for duplicates
    logger.info("\nChecking for duplicates...")
    duplicates = validator.check_duplicates()
    if duplicates:
        logger.warning(f"Found {len(duplicates)} duplicate entries")
        for dup in duplicates:
            logger.warning(f"Duplicate {dup['type']}: {dup['value']} (IDs: {', '.join(dup['ids'])})")
    
    # Check related data
    logger.info("\nChecking related data...")
    related_data = validator.check_related_data()
    for field, ids in related_data.items():
        if ids:
            logger.warning(f"Found {len(ids)} schemes with missing {field}")
    
    # Export data for manual review
    logger.info("\nExporting data for manual review...")
    validator.export_to_json()

if __name__ == "__main__":
    main() 