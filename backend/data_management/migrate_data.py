import json
import os
import sqlite3
from typing import Dict, List
import logging
from database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Category mapping with icons and colors
CATEGORY_MAPPING = {
    "women_and_child": {
        "id": 1,
        "name": "Women & Child",
        "icon": "users",
        "color": "#FF69B4",
        "description": "Schemes for women and children welfare"
    },
    "utility_sanitation": {
        "id": 2,
        "name": "Utility & Sanitation",
        "icon": "droplet",
        "color": "#4169E1",
        "description": "Schemes related to utilities and sanitation"
    },
    "travel_tourism": {
        "id": 3,
        "name": "Travel & Tourism",
        "icon": "plane",
        "color": "#FFA500",
        "description": "Schemes for travel and tourism development"
    },
    "transport_infrastructure": {
        "id": 4,
        "name": "Transport & Infrastructure",
        "icon": "road",
        "color": "#808080",
        "description": "Schemes for transport and infrastructure development"
    },
    "sports_culture": {
        "id": 5,
        "name": "Sports & Culture",
        "icon": "trophy",
        "color": "#FFD700",
        "description": "Schemes for sports and cultural development"
    },
    "social_welfare_empowerment": {
        "id": 6,
        "name": "Social Welfare & Empowerment",
        "icon": "heart",
        "color": "#FF4500",
        "description": "Schemes for social welfare and empowerment"
    },
    "skills_employment": {
        "id": 7,
        "name": "Skills & Employment",
        "icon": "briefcase",
        "color": "#32CD32",
        "description": "Schemes for skill development and employment"
    },
    "science_it_communications": {
        "id": 8,
        "name": "Science, IT & Communications",
        "icon": "cpu",
        "color": "#4B0082",
        "description": "Schemes for science, IT and communications"
    },
    "public_safety_law_justice": {
        "id": 9,
        "name": "Public Safety, Law & Justice",
        "icon": "shield",
        "color": "#000080",
        "description": "Schemes for public safety, law and justice"
    },
    "housing_shelter": {
        "id": 10,
        "name": "Housing & Shelter",
        "icon": "home",
        "color": "#8B4513",
        "description": "Schemes for housing and shelter"
    },
    "health_wellness": {
        "id": 11,
        "name": "Health & Wellness",
        "icon": "heart-pulse",
        "color": "#FF0000",
        "description": "Schemes for health and wellness"
    },
    "education_learning": {
        "id": 12,
        "name": "Education & Learning",
        "icon": "book-open",
        "color": "#008000",
        "description": "Schemes for education and learning"
    },
    "business_entrepreneurship": {
        "id": 13,
        "name": "Business & Entrepreneurship",
        "icon": "building",
        "color": "#800080",
        "description": "Schemes for business and entrepreneurship"
    },
    "banking_financial_services_and_insurance": {
        "id": 14,
        "name": "Banking & Financial Services",
        "icon": "banknote",
        "color": "#006400",
        "description": "Schemes for banking and financial services"
    },
    "agriculture_rural_environment": {
        "id": 15,
        "name": "Agriculture & Rural Development",
        "icon": "tractor",
        "color": "#228B22",
        "description": "Schemes for agriculture and rural development"
    }
}

def load_json_data(file_path: str) -> List[Dict]:
    """Load data from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        return []

def clear_database(db_path: str):
    """Clear all data from the database."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Disable foreign key constraints temporarily
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Clear all tables
        cursor.execute("DELETE FROM scheme_tags")
        cursor.execute("DELETE FROM tags")
        cursor.execute("DELETE FROM schemes")
        cursor.execute("DELETE FROM categories")
        
        # Reset autoincrement counters if sqlite_sequence exists
        try:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('schemes', 'tags')")
        except sqlite3.OperationalError:
            # sqlite_sequence table doesn't exist, which is fine
            pass
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        conn.commit()

def migrate_data():
    """Migrate data from JSON files to the database."""
    db = Database(db_path="yojnabuddy.db")
    
    # Clear existing data
    logger.info("Clearing existing data...")
    clear_database(db.db_path)
    
    # First, create categories
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        # Insert categories
        for category_key, category_data in CATEGORY_MAPPING.items():
            cursor.execute('''
                INSERT INTO categories (id, name, description, icon, color)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                category_data['id'],
                category_data['name'],
                category_data['description'],
                category_data['icon'],
                category_data['color']
            ))
        
        conn.commit()
    
    # Process each category file
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'category_data')
    
    for filename in os.listdir(data_dir):
        if not filename.endswith('.json'):
            continue
            
        category_key = filename.replace('.json', '')
        category_id = CATEGORY_MAPPING[category_key]['id']
        file_path = os.path.join(data_dir, filename)
        schemes = load_json_data(file_path)
        
        logger.info(f"Processing {len(schemes)} schemes from {filename}")
        
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            for scheme in schemes:
                try:
                    # Insert scheme
                    cursor.execute('''
                        INSERT OR REPLACE INTO schemes (
                            id, title, description, ministry, category_id,
                            scheme_type, eligibility, benefits,
                            documents_required, application_process,
                            website, helpline
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        int(scheme.get('id', 0)),
                        scheme.get('name', ''),
                        scheme.get('description', ''),
                        scheme.get('state', ''),  # Using state as ministry
                        category_id,
                        'central' if 'Ministry' in scheme.get('state', '') else 'state',
                        '\n'.join(scheme.get('eligibility_criteria', [])),
                        '\n'.join(scheme.get('benefits', [])),
                        '\n'.join(scheme.get('required_documents', [])),
                        '',  # application_process not in data
                        scheme.get('url', ''),
                        ''  # helpline not in data
                    ))
                    
                    scheme_id = int(scheme.get('id', 0))
                    
                    # Insert FAQs as tags
                    if 'faqs' in scheme and isinstance(scheme['faqs'], list):
                        for faq in scheme['faqs']:
                            # Create a tag from the FAQ question
                            tag_name = f"FAQ: {faq['question'][:50]}..."  # Truncate long questions
                            
                            # Insert tag if it doesn't exist
                            cursor.execute('''
                                INSERT OR IGNORE INTO tags (name)
                                VALUES (?)
                            ''', (tag_name,))
                            
                            # Get tag id
                            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
                            tag_id = cursor.fetchone()[0]
                            
                            # Create scheme-tag relationship
                            cursor.execute('''
                                INSERT OR IGNORE INTO scheme_tags (scheme_id, tag_id)
                                VALUES (?, ?)
                            ''', (scheme_id, tag_id))
                except Exception as e:
                    logger.error(f"Error processing scheme {scheme.get('id', 'unknown')}: {str(e)}")
                    continue
            
            conn.commit()
            logger.info(f"Completed processing {filename}")

if __name__ == '__main__':
    logger.info("Starting data migration...")
    migrate_data()
    logger.info("Data migration completed!") 