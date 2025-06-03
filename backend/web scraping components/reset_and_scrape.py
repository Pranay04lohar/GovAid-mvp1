import os
import sqlite3
import logging
from web_scraping_components.batch_scraper import process_all_categories

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def reset_database():
    """Reset the database by dropping all tables and recreating them."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "yojnabuddy.db")
    
    # Delete the existing database file
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info("Deleted existing database file")
    
    # Create new database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS schemes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        url TEXT UNIQUE NOT NULL,
        last_updated TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_id INTEGER,
        category TEXT NOT NULL,
        FOREIGN KEY (scheme_id) REFERENCES schemes (id)
    );

    CREATE TABLE IF NOT EXISTS benefits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_id INTEGER,
        benefit TEXT NOT NULL,
        FOREIGN KEY (scheme_id) REFERENCES schemes (id)
    );

    CREATE TABLE IF NOT EXISTS eligibility_criteria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_id INTEGER,
        criterion TEXT NOT NULL,
        FOREIGN KEY (scheme_id) REFERENCES schemes (id)
    );

    CREATE TABLE IF NOT EXISTS required_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_id INTEGER,
        document TEXT NOT NULL,
        FOREIGN KEY (scheme_id) REFERENCES schemes (id)
    );

    CREATE TABLE IF NOT EXISTS faqs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_id INTEGER,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        FOREIGN KEY (scheme_id) REFERENCES schemes (id)
    );
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Created new database with tables")

def main():
    # Reset database
    logger.info("Resetting database...")
    reset_database()
    
    # Run scraper
    logger.info("Starting scraper with new numbers...")
    process_all_categories()

if __name__ == "__main__":
    main() 