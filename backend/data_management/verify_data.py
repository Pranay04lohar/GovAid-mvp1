import sqlite3
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_data():
    """Verify the migrated data in the database."""
    with sqlite3.connect("schemes.db") as conn:
        cursor = conn.cursor()
        
        # Check categories
        cursor.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]
        logger.info(f"Total categories: {category_count}")
        
        # Check schemes
        cursor.execute("SELECT COUNT(*) FROM schemes")
        scheme_count = cursor.fetchone()[0]
        logger.info(f"Total schemes: {scheme_count}")
        
        # Check tags
        cursor.execute("SELECT COUNT(*) FROM tags")
        tag_count = cursor.fetchone()[0]
        logger.info(f"Total tags: {tag_count}")
        
        # Check scheme tags
        cursor.execute("SELECT COUNT(*) FROM scheme_tags")
        scheme_tag_count = cursor.fetchone()[0]
        logger.info(f"Total scheme-tag relationships: {scheme_tag_count}")
        
        # Check schemes per category
        cursor.execute("""
            SELECT c.name, COUNT(s.id) as scheme_count
            FROM categories c
            LEFT JOIN schemes s ON c.id = s.category_id
            GROUP BY c.id
            ORDER BY scheme_count DESC
        """)
        logger.info("\nSchemes per category:")
        for category, count in cursor.fetchall():
            logger.info(f"{category}: {count} schemes")
        
        # Check scheme types
        cursor.execute("""
            SELECT scheme_type, COUNT(*) as count
            FROM schemes
            GROUP BY scheme_type
        """)
        logger.info("\nScheme types:")
        for scheme_type, count in cursor.fetchall():
            logger.info(f"{scheme_type}: {count} schemes")

if __name__ == '__main__':
    logger.info("Starting data verification...")
    verify_data()
    logger.info("Data verification completed!") 