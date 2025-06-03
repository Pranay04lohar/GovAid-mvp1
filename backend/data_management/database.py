import sqlite3
from typing import Dict, List, Optional
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "yojnabuddy.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    icon TEXT,
                    color TEXT
                )
            ''')
            
            # Create schemes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schemes (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    ministry TEXT,
                    category_id INTEGER,
                    scheme_type TEXT CHECK(scheme_type IN ('state', 'central')),
                    eligibility TEXT,
                    benefits TEXT,
                    documents_required TEXT,
                    application_process TEXT,
                    website TEXT,
                    helpline TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            ''')
            
            # Create tags table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            
            # Create scheme_tags table for many-to-many relationship
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheme_tags (
                    scheme_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (scheme_id, tag_id),
                    FOREIGN KEY (scheme_id) REFERENCES schemes(id),
                    FOREIGN KEY (tag_id) REFERENCES tags(id)
                )
            ''')
            
            conn.commit()

    def get_all_categories_with_counts(self) -> List[Dict]:
        """Get all categories with their scheme counts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.id, c.name, c.description, c.icon, c.color,
                       COUNT(s.id) as scheme_count
                FROM categories c
                LEFT JOIN schemes s ON c.id = s.category_id
                GROUP BY c.id
                ORDER BY c.name
            ''')
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "icon": row[3],
                    "color": row[4],
                    "schemeCount": row[5]
                }
                for row in rows
            ]

    def get_schemes_by_category(
        self,
        category_id: int,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = 'relevance'
    ) -> List[Dict]:
        """Get schemes by category with pagination and sorting."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Base query
            query = '''
                SELECT s.id, s.title, s.description, s.ministry, s.scheme_type,
                       GROUP_CONCAT(t.name) as tags
                FROM schemes s
                LEFT JOIN scheme_tags st ON s.id = st.scheme_id
                LEFT JOIN tags t ON st.tag_id = t.id
                WHERE s.category_id = ?
                GROUP BY s.id
            '''
            
            # Add sorting
            if sort_by == 'newest':
                query += ' ORDER BY s.created_at DESC'
            elif sort_by == 'alphabetical':
                query += ' ORDER BY s.title ASC'
            else:  # relevance
                query += ' ORDER BY s.id DESC'
            
            # Add pagination
            query += ' LIMIT ? OFFSET ?'
            
            cursor.execute(query, (category_id, limit, offset))
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "ministry": row[3],
                    "type": row[4],
                    "tags": row[5].split(',') if row[5] else []
                }
                for row in rows
            ]

    def get_scheme_details(self, scheme_id: int) -> Optional[Dict]:
        """Get detailed information about a specific scheme."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.id, s.title, s.description, s.ministry, s.scheme_type,
                       s.eligibility, s.benefits, s.documents_required,
                       s.application_process, s.website, s.helpline,
                       c.name as category_name,
                       GROUP_CONCAT(t.name) as tags
                FROM schemes s
                LEFT JOIN categories c ON s.category_id = c.id
                LEFT JOIN scheme_tags st ON s.id = st.scheme_id
                LEFT JOIN tags t ON st.tag_id = t.id
                WHERE s.id = ?
                GROUP BY s.id
            ''', (scheme_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            return {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "ministry": row[3],
                "type": row[4],
                "eligibility": row[5],
                "benefits": row[6],
                "documentsRequired": row[7],
                "applicationProcess": row[8],
                "website": row[9],
                "helpline": row[10],
                "category": row[11],
                "tags": row[12].split(',') if row[12] else []
            }

    def get_schemes_by_category_and_type(
        self,
        category_id: int,
        scheme_type: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict]:
        """Get schemes by category and type (state/central) with pagination."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.id, s.title, s.description, s.ministry, s.scheme_type,
                       GROUP_CONCAT(t.name) as tags
                FROM schemes s
                LEFT JOIN scheme_tags st ON s.id = st.scheme_id
                LEFT JOIN tags t ON st.tag_id = t.id
                WHERE s.category_id = ? AND s.scheme_type = ?
                GROUP BY s.id
                ORDER BY s.created_at DESC
                LIMIT ? OFFSET ?
            ''', (category_id, scheme_type, limit, offset))
            
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "ministry": row[3],
                    "type": row[4],
                    "tags": row[5].split(',') if row[5] else []
                }
                for row in rows
            ]

    def get_scheme_count_by_category(self, category_id: int) -> int:
        """Get total count of schemes in a category."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM schemes WHERE category_id = ?
            ''', (category_id,))
            return cursor.fetchone()[0]

    def get_scheme_count_by_category_and_type(
        self,
        category_id: int,
        scheme_type: str
    ) -> int:
        """Get total count of schemes in a category by type."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM schemes 
                WHERE category_id = ? AND scheme_type = ?
            ''', (category_id, scheme_type))
            return cursor.fetchone()[0]

    def save_scheme(self, scheme_data: Dict) -> Optional[int]:
        """Save a scheme and its related data to the database."""
        try:
            cursor = self.conn.cursor()
            
            # Check if scheme already exists
            cursor.execute('SELECT id FROM schemes WHERE url = ?', (scheme_data['url'],))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing scheme
                scheme_id = existing['id']
                cursor.execute('''
                UPDATE schemes 
                SET name = ?, description = ?, state = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (scheme_data['name'], scheme_data['description'], 
                      scheme_data['state'], scheme_id))
                
                # Delete existing related data
                for table in ['categories', 'benefits', 'eligibility_criteria', 
                            'application_process', 'required_documents', 'faqs']:
                    cursor.execute(f'DELETE FROM {table} WHERE scheme_id = ?', (scheme_id,))
            else:
                # Insert new scheme
                cursor.execute('''
                INSERT INTO schemes (name, description, state, url)
                VALUES (?, ?, ?, ?)
                ''', (scheme_data['name'], scheme_data['description'], 
                      scheme_data['state'], scheme_data['url']))
                scheme_id = cursor.lastrowid
            
            # Insert categories
            for category in scheme_data.get('categories', []):
                cursor.execute('''
                INSERT INTO categories (scheme_id, category)
                VALUES (?, ?)
                ''', (scheme_id, category))
            
            # Insert benefits
            for benefit in scheme_data.get('benefits', []):
                cursor.execute('''
                INSERT INTO benefits (scheme_id, benefit)
                VALUES (?, ?)
                ''', (scheme_id, benefit))
            
            # Insert eligibility criteria
            for criterion in scheme_data.get('eligibility_criteria', []):
                cursor.execute('''
                INSERT INTO eligibility_criteria (scheme_id, criterion)
                VALUES (?, ?)
                ''', (scheme_id, criterion))
            
            # Insert application process steps
            for step in scheme_data.get('application_process', []):
                cursor.execute('''
                INSERT INTO application_process (scheme_id, step)
                VALUES (?, ?)
                ''', (scheme_id, step))
            
            # Insert required documents
            for doc in scheme_data.get('required_documents', []):
                cursor.execute('''
                INSERT INTO required_documents (scheme_id, document)
                VALUES (?, ?)
                ''', (scheme_id, doc))
            
            # Insert FAQs
            for faq in scheme_data.get('faqs', []):
                cursor.execute('''
                INSERT INTO faqs (scheme_id, question, answer)
                VALUES (?, ?, ?)
                ''', (scheme_id, faq['question'], faq['answer']))
            
            self.conn.commit()
            logger.info(f"Scheme saved successfully: {scheme_data['name']}")
            return scheme_id
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error saving scheme: {str(e)}")
            return None

    def get_scheme_by_url(self, url: str) -> Optional[Dict]:
        """Get a scheme and all its related data by URL."""
        try:
            cursor = self.conn.cursor()
            
            # Get scheme details
            cursor.execute('SELECT * FROM schemes WHERE url = ?', (url,))
            scheme = cursor.fetchone()
            
            if not scheme:
                return None
            
            # Get all related data
            scheme_data = dict(scheme)
            
            # Get categories
            cursor.execute('SELECT category FROM categories WHERE scheme_id = ?', (scheme['id'],))
            scheme_data['categories'] = [row['category'] for row in cursor.fetchall()]
            
            # Get benefits
            cursor.execute('SELECT benefit FROM benefits WHERE scheme_id = ?', (scheme['id'],))
            scheme_data['benefits'] = [row['benefit'] for row in cursor.fetchall()]
            
            # Get eligibility criteria
            cursor.execute('SELECT criterion FROM eligibility_criteria WHERE scheme_id = ?', (scheme['id'],))
            scheme_data['eligibility_criteria'] = [row['criterion'] for row in cursor.fetchall()]
            
            # Get application process
            cursor.execute('SELECT step FROM application_process WHERE scheme_id = ?', (scheme['id'],))
            scheme_data['application_process'] = [row['step'] for row in cursor.fetchall()]
            
            # Get required documents
            cursor.execute('SELECT document FROM required_documents WHERE scheme_id = ?', (scheme['id'],))
            scheme_data['required_documents'] = [row['document'] for row in cursor.fetchall()]
            
            # Get FAQs
            cursor.execute('SELECT question, answer FROM faqs WHERE scheme_id = ?', (scheme['id'],))
            scheme_data['faqs'] = [dict(row) for row in cursor.fetchall()]
            
            return scheme_data
            
        except Exception as e:
            logger.error(f"Error getting scheme: {str(e)}")
            return None

    def get_all_schemes(self) -> List[Dict]:
        """Get all schemes with their basic information."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM schemes ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all schemes: {str(e)}")
            return []

    def search_schemes(self, query: str, params: List = None) -> List[Dict]:
        """Search schemes by name, description, or state.
        
        Args:
            query: Either a search term or a custom SQL query
            params: Optional list of parameters for the custom query
        """
        try:
            cursor = self.conn.cursor()
            
            if params is None:
                # Simple keyword search
                search_term = f"%{query}%"
                cursor.execute('''
                SELECT DISTINCT s.*, 
                       GROUP_CONCAT(DISTINCT c.category) as categories
                FROM schemes s
                LEFT JOIN categories c ON s.id = c.scheme_id
                WHERE s.name LIKE ? OR s.description LIKE ? OR s.state LIKE ?
                GROUP BY s.id
                ORDER BY s.name
                ''', (search_term, search_term, search_term))
            else:
                # Custom query with parameters
                cursor.execute(query, params)
            
            schemes = []
            for row in cursor.fetchall():
                scheme = dict(row)
                if 'categories' in scheme:
                    scheme['categories'] = scheme['categories'].split(',') if scheme['categories'] else []
                schemes.append(scheme)
            
            return schemes
        except Exception as e:
            logger.error(f"Error searching schemes: {str(e)}")
            return []

    def get_schemes_by_state(self, state: str) -> List[Dict]:
        """Get all schemes for a specific state."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM schemes WHERE state = ? ORDER BY created_at DESC', (state,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting schemes by state: {str(e)}")
            return []

    def get_scheme_by_id(self, scheme_id: int) -> Optional[Dict]:
        """Get a scheme and all its related data by ID."""
        try:
            cursor = self.conn.cursor()
            
            # Get scheme details
            cursor.execute('SELECT * FROM schemes WHERE id = ?', (scheme_id,))
            scheme = cursor.fetchone()
            
            if not scheme:
                return None
            
            # Get all related data
            scheme_data = dict(scheme)
            
            # Get categories
            cursor.execute('SELECT category FROM categories WHERE scheme_id = ?', (scheme_id,))
            scheme_data['categories'] = [row['category'] for row in cursor.fetchall()]
            
            # Get benefits
            cursor.execute('SELECT benefit FROM benefits WHERE scheme_id = ?', (scheme_id,))
            scheme_data['benefits'] = [row['benefit'] for row in cursor.fetchall()]
            
            # Get eligibility criteria
            cursor.execute('SELECT criterion FROM eligibility_criteria WHERE scheme_id = ?', (scheme_id,))
            scheme_data['eligibility_criteria'] = [row['criterion'] for row in cursor.fetchall()]
            
            # Get application process
            cursor.execute('SELECT step FROM application_process WHERE scheme_id = ?', (scheme_id,))
            scheme_data['application_process'] = [row['step'] for row in cursor.fetchall()]
            
            # Get required documents
            cursor.execute('SELECT document FROM required_documents WHERE scheme_id = ?', (scheme_id,))
            scheme_data['required_documents'] = [row['document'] for row in cursor.fetchall()]
            
            # Get FAQs
            cursor.execute('SELECT question, answer FROM faqs WHERE scheme_id = ?', (scheme_id,))
            scheme_data['faqs'] = [dict(row) for row in cursor.fetchall()]
            
            return scheme_data
            
        except Exception as e:
            logger.error(f"Error getting scheme by ID: {str(e)}")
            return None

    def get_all_categories(self) -> List[str]:
        """Get all unique categories."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM categories ORDER BY category")
            return [row['category'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            return []

    def get_all_states(self) -> List[str]:
        """Get all unique states."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT state FROM schemes ORDER BY state")
            return [row['state'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting states: {str(e)}")
            return []

    def search_schemes_by_keyword(self, keyword: str) -> List[Dict]:
        """Search schemes by keyword in name, description, or state."""
        try:
            cursor = self.conn.cursor()
            search_term = f"%{keyword}%"
            
            cursor.execute("""
            SELECT DISTINCT s.*, 
                   GROUP_CONCAT(DISTINCT c.category) as categories
            FROM schemes s
            LEFT JOIN categories c ON s.id = c.scheme_id
            WHERE s.name LIKE ? 
               OR s.description LIKE ? 
               OR s.state LIKE ?
            GROUP BY s.id
            ORDER BY s.name
            """, (search_term, search_term, search_term))
            
            schemes = []
            for row in cursor.fetchall():
                scheme = dict(row)
                scheme['categories'] = scheme['categories'].split(',') if scheme['categories'] else []
                schemes.append(scheme)
            
            return schemes
        except Exception as e:
            logger.error(f"Error searching schemes: {str(e)}")
            return []

    def get_schemes_by_category(self, category: str) -> List[Dict]:
        """Get all schemes for a specific category."""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
            SELECT DISTINCT s.*, 
                   GROUP_CONCAT(DISTINCT c.category) as categories
            FROM schemes s
            JOIN categories c ON s.id = c.scheme_id
            WHERE c.category = ?
            GROUP BY s.id
            ORDER BY s.name
            """, (category,))
            
            schemes = []
            for row in cursor.fetchall():
                scheme = dict(row)
                scheme['categories'] = scheme['categories'].split(',') if scheme['categories'] else []
                schemes.append(scheme)
            
            return schemes
        except Exception as e:
            logger.error(f"Error getting schemes by category: {str(e)}")
            return []

    def get_count(self, query: str, params: List) -> int:
        """Get count from a query."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()['total']
        except Exception as e:
            logger.error(f"Error getting count: {str(e)}")
            return 0

    def __del__(self):
        """Close database connection when object is destroyed."""
        if hasattr(self, 'conn'):
            self.conn.close() 