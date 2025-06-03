import logging
from database import Database
import json
import os
from datetime import datetime
from typing import Dict, List, Set
import requests
from bs4 import BeautifulSoup
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataFixer:
    def __init__(self):
        self.db = Database()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_schemes_with_missing_data(self) -> Dict[str, List[Dict]]:
        """Get schemes with missing documents or FAQs."""
        try:
            cursor = self.db.conn.cursor()
            
            # Get schemes with missing documents
            cursor.execute("""
            SELECT s.*, GROUP_CONCAT(DISTINCT c.category) as categories
            FROM schemes s
            LEFT JOIN categories c ON s.id = c.scheme_id
            LEFT JOIN required_documents rd ON s.id = rd.scheme_id
            WHERE rd.id IS NULL
            GROUP BY s.id
            """)
            missing_docs = [dict(row) for row in cursor.fetchall()]
            
            # Get schemes with missing FAQs
            cursor.execute("""
            SELECT s.*, GROUP_CONCAT(DISTINCT c.category) as categories
            FROM schemes s
            LEFT JOIN categories c ON s.id = c.scheme_id
            LEFT JOIN faqs f ON s.id = f.scheme_id
            WHERE f.id IS NULL
            GROUP BY s.id
            """)
            missing_faqs = [dict(row) for row in cursor.fetchall()]
            
            return {
                'missing_documents': missing_docs,
                'missing_faqs': missing_faqs
            }
        except Exception as e:
            logger.error(f"Error getting schemes with missing data: {str(e)}")
            return {'missing_documents': [], 'missing_faqs': []}

    def get_extra_urls(self) -> Set[str]:
        """Get URLs that are in the database but not in JSON files."""
        try:
            # Get URLs from database
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT url FROM schemes")
            db_urls = {row['url'] for row in cursor.fetchall()}
            print(f"\nTotal URLs in database: {len(db_urls)}")
            
            # Get URLs from JSON files
            json_urls = set()
            json_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data_export")
            
            if not os.path.exists(json_dir):
                logger.warning(f"JSON directory not found: {json_dir}")
                return db_urls  # Return all DB URLs if we can't find JSON files
            
            print(f"\nSearching for JSON files in: {json_dir}")
            for filename in os.listdir(json_dir):
                if filename.endswith('.json'):
                    try:
                        file_path = os.path.join(json_dir, filename)
                        print(f"\nReading file: {filename}")
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                for item in data:
                                    if isinstance(item, dict) and 'url' in item:
                                        json_urls.add(item['url'])
                            elif isinstance(data, dict):
                                # Handle different JSON structures
                                if 'schemes' in data:
                                    for scheme in data['schemes']:
                                        if isinstance(scheme, dict) and 'url' in scheme:
                                            json_urls.add(scheme['url'])
                                elif 'url' in data:
                                    json_urls.add(data['url'])
                    except Exception as e:
                        logger.error(f"Error reading {filename}: {str(e)}")
            
            print(f"\nTotal URLs in JSON files: {len(json_urls)}")
            extra_urls = db_urls - json_urls
            print(f"Found {len(extra_urls)} extra URLs in DB")
            
            # Print some example URLs for verification
            if extra_urls:
                print("\nExample extra URLs:")
                for url in list(extra_urls)[:5]:
                    print(f"- {url}")
            
            return extra_urls
        except Exception as e:
            logger.error(f"Error getting extra URLs: {str(e)}")
            return set()

    def scrape_missing_data(self, url: str) -> Dict:
        """Scrape missing documents and FAQs from a scheme's URL."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"\nAnalyzing page: {url}")
            
            # Extract documents (try multiple possible structures)
            documents = set()  # Use set to avoid duplicates
            
            # First try to find the main content area
            main_content = soup.find('main') or soup.find('div', {'class': 'content'}) or soup.find('div', {'class': 'main-content'})
            if main_content:
                # Look for document lists in the main content
                doc_sections = [
                    main_content.find('div', string=lambda x: x and 'required documents' in x.lower()),
                    main_content.find('div', string=lambda x: x and 'documents required' in x.lower()),
                    main_content.find('div', string=lambda x: x and 'documents needed' in x.lower()),
                    main_content.find('div', string=lambda x: x and 'documents' in x.lower() and 'list' in x.lower()),
                    main_content.find('section', string=lambda x: x and 'required documents' in x.lower()),
                    main_content.find('h2', string=lambda x: x and 'required documents' in x.lower()),
                    main_content.find('h3', string=lambda x: x and 'required documents' in x.lower())
                ]
                
                for section in doc_sections:
                    if section:
                        print(f"\nFound document section: {section.name} with class: {section.get('class', 'no-class')}")
                        # Look for the next sibling that contains the actual list
                        list_container = section.find_next(['ul', 'ol', 'div'])
                        if list_container:
                            # Try different list structures
                            for item in list_container.find_all(['li', 'p', 'div', 'span']):
                                text = item.text.strip()
                                # Skip placeholder text, very short items, and false positives
                                if (text and len(text) > 5 and 
                                    'no documents required' not in text.lower() and
                                    'documents required' not in text.lower() and
                                    'documents needed' not in text.lower() and
                                    'make sure' not in text.lower() and
                                    'applicant' not in text.lower() and
                                    'frequently asked questions' not in text.lower() and
                                    'faq' not in text.lower() and
                                    'common questions' not in text.lower() and
                                    'questions' not in text.lower() and
                                    'answers' not in text.lower()):
                                    print(f"Found document: {text}")
                                    documents.add(text)
                        if documents:  # If we found documents, no need to check other sections
                            break
                
                # If no documents found in sections, try looking for document lists directly
                if not documents:
                    # Look for common document list patterns
                    doc_lists = main_content.find_all(['ul', 'ol'], class_=lambda x: x and any(c in str(x).lower() for c in ['doc', 'list', 'required']))
                    for doc_list in doc_lists:
                        for item in doc_list.find_all('li'):
                            text = item.text.strip()
                            if (text and len(text) > 5 and 
                                'no documents required' not in text.lower() and
                                'documents required' not in text.lower() and
                                'documents needed' not in text.lower() and
                                'make sure' not in text.lower() and
                                'applicant' not in text.lower() and
                                'frequently asked questions' not in text.lower() and
                                'faq' not in text.lower() and
                                'common questions' not in text.lower() and
                                'questions' not in text.lower() and
                                'answers' not in text.lower()):
                                print(f"Found document: {text}")
                                documents.add(text)
            
            # Extract FAQs (try multiple possible structures)
            faqs = []
            seen_questions = set()  # Track seen questions to avoid duplicates
            
            # First try to find the main content area
            main_content = soup.find('main') or soup.find('div', {'class': 'content'}) or soup.find('div', {'class': 'main-content'})
            if main_content:
                # Look for FAQ sections in the main content
                faq_sections = [
                    main_content.find('div', string=lambda x: x and 'frequently asked questions' in x.lower()),
                    main_content.find('div', string=lambda x: x and 'faq' in x.lower()),
                    main_content.find('div', string=lambda x: x and 'common questions' in x.lower()),
                    main_content.find('section', string=lambda x: x and 'faq' in x.lower()),
                    main_content.find('h2', string=lambda x: x and 'faq' in x.lower()),
                    main_content.find('h3', string=lambda x: x and 'faq' in x.lower())
                ]
                
                for section in faq_sections:
                    if section:
                        print(f"\nFound FAQ section: {section.name} with class: {section.get('class', 'no-class')}")
                        # Look for the next sibling that contains the actual FAQs
                        faq_container = section.find_next(['div', 'section'])
                        if faq_container:
                            # Try different FAQ item structures
                            for item in faq_container.find_all(['div', 'article', 'section']):
                                # Try to find question
                                q_elem = item.find(['h3', 'h4', 'strong', 'b', 'span'])
                                if not q_elem:
                                    # Try to find question in the first paragraph
                                    q_elem = item.find('p')
                                
                                # Try to find answer
                                a_elem = None
                                if q_elem:
                                    # Look for answer in the next sibling
                                    a_elem = q_elem.find_next(['p', 'div', 'span'])
                                
                                if q_elem and a_elem:
                                    question = q_elem.text.strip()
                                    answer = a_elem.text.strip()
                                    
                                    # Only add if we have both question and answer, and haven't seen this question before
                                    if (question and answer and 
                                        question not in seen_questions and
                                        len(question) > 5 and  # Avoid very short questions
                                        len(answer) > 5):  # Avoid very short answers
                                        seen_questions.add(question)
                                        print(f"Found FAQ: Q: {question[:50]}... A: {answer[:50]}...")
                                        faqs.append({
                                            'question': question,
                                            'answer': answer
                                        })
                        if faqs:  # If we found FAQs, no need to check other sections
                            break
            
            logger.info(f"Found {len(documents)} documents and {len(faqs)} FAQs for {url}")
            return {
                'documents': list(documents),  # Convert set back to list
                'faqs': faqs
            }
        except Exception as e:
            logger.error(f"Error scraping data from {url}: {str(e)}")
            return {'documents': [], 'faqs': []}

    def update_scheme_data(self, scheme_id: int, data: Dict) -> bool:
        """Update a scheme with missing documents and FAQs."""
        try:
            cursor = self.db.conn.cursor()
            
            # Update documents
            for doc in data['documents']:
                cursor.execute('''
                INSERT INTO required_documents (scheme_id, document)
                VALUES (?, ?)
                ''', (scheme_id, doc))
            
            # Update FAQs
            for faq in data['faqs']:
                cursor.execute('''
                INSERT INTO faqs (scheme_id, question, answer)
                VALUES (?, ?, ?)
                ''', (scheme_id, faq['question'], faq['answer']))
            
            self.db.conn.commit()
            return True
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Error updating scheme {scheme_id}: {str(e)}")
            return False

    def fix_missing_data(self):
        """Fix missing documents and FAQs for all affected schemes."""
        missing_data = self.get_schemes_with_missing_data()
        
        # Fix missing documents
        logger.info(f"Found {len(missing_data['missing_documents'])} schemes with missing documents")
        for scheme in missing_data['missing_documents']:
            logger.info(f"Fixing documents for scheme: {scheme['name']}")
            data = self.scrape_missing_data(scheme['url'])
            if data['documents']:
                if self.update_scheme_data(scheme['id'], {'documents': data['documents'], 'faqs': []}):
                    logger.info(f"Updated documents for scheme: {scheme['name']}")
            time.sleep(1)  # Be nice to the server
        
        # Fix missing FAQs
        logger.info(f"Found {len(missing_data['missing_faqs'])} schemes with missing FAQs")
        for scheme in missing_data['missing_faqs']:
            logger.info(f"Fixing FAQs for scheme: {scheme['name']}")
            data = self.scrape_missing_data(scheme['url'])
            if data['faqs']:
                if self.update_scheme_data(scheme['id'], {'documents': [], 'faqs': data['faqs']}):
                    logger.info(f"Updated FAQs for scheme: {scheme['name']}")
            time.sleep(1)  # Be nice to the server

    def fix_url_sync(self):
        """Fix URL synchronization between database and JSON files."""
        try:
            extra_urls = self.get_extra_urls()
            if not extra_urls:
                logger.info("No URL synchronization issues found")
                return
            
            logger.info(f"Found {len(extra_urls)} URLs to fix")
            
            # Create a backup of the database
            backup_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                     f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            self.db.conn.backup(backup_path)
            logger.info(f"Created database backup at: {backup_path}")
            
            # Remove extra URLs from database
            cursor = self.db.conn.cursor()
            for url in extra_urls:
                try:
                    # First remove related data
                    cursor.execute("DELETE FROM categories WHERE scheme_id IN (SELECT id FROM schemes WHERE url = ?)", (url,))
                    cursor.execute("DELETE FROM required_documents WHERE scheme_id IN (SELECT id FROM schemes WHERE url = ?)", (url,))
                    cursor.execute("DELETE FROM faqs WHERE scheme_id IN (SELECT id FROM schemes WHERE url = ?)", (url,))
                    # Then remove the scheme
                    cursor.execute("DELETE FROM schemes WHERE url = ?", (url,))
                except Exception as e:
                    logger.error(f"Error removing URL {url}: {str(e)}")
                    continue
            
            self.db.conn.commit()
            logger.info(f"Removed {len(extra_urls)} extra URLs from database")
            
            # Verify the fix
            remaining_extra_urls = self.get_extra_urls()
            if not remaining_extra_urls:
                logger.info("URL synchronization fixed successfully")
            else:
                logger.warning(f"Still found {len(remaining_extra_urls)} extra URLs after fix")
        
        except Exception as e:
            logger.error(f"Error fixing URL synchronization: {str(e)}")
            if os.path.exists(backup_path):
                logger.info("Restoring from backup...")
                self.db.conn.close()
                os.remove(self.db.db_path)
                os.rename(backup_path, self.db.db_path)
                self.db = Database()  # Reinitialize database connection

    def investigate_extra_urls(self):
        """Investigate URLs that are in the database but not in JSON files."""
        extra_urls = self.get_extra_urls()
        logger.info(f"Found {len(extra_urls)} extra URLs in the database")
        
        # Create a report of extra URLs
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_extra_urls': len(extra_urls),
            'urls': list(extra_urls)
        }
        
        # Save report
        report_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"extra_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Saved extra URLs report to: {report_path}")
        
        # Check if these URLs are still valid
        valid_urls = []
        invalid_urls = []
        
        for url in extra_urls:
            try:
                response = self.session.head(url, allow_redirects=True)
                if response.status_code == 200:
                    valid_urls.append(url)
                else:
                    invalid_urls.append({
                        'url': url,
                        'status_code': response.status_code
                    })
            except Exception as e:
                invalid_urls.append({
                    'url': url,
                    'error': str(e)
                })
            time.sleep(1)  # Be nice to the server
        
        # Update report with validation results
        report['valid_urls'] = valid_urls
        report['invalid_urls'] = invalid_urls
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Found {len(valid_urls)} valid URLs and {len(invalid_urls)} invalid URLs")
        return report

def main():
    fixer = DataFixer()
    
    # Fix missing data
    logger.info("Starting to fix missing data...")
    fixer.fix_missing_data()
    
    # Fix URL synchronization
    logger.info("Starting URL synchronization fix...")
    fixer.fix_url_sync()
    
    # Investigate extra URLs
    logger.info("Starting investigation of extra URLs...")
    report = fixer.investigate_extra_urls()
    
    logger.info("Data fixing and investigation complete!")

if __name__ == '__main__':
    main() 