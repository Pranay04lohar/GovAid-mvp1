from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from typing import List, Dict, Any, Optional
import os
# from api.my_blueprint import my_blueprint # Old import
from my_blueprint import my_blueprint # Corrected import for sibling modules

app = Flask(__name__)
CORS(app)


print(app.url_map)  # <-- Add this line

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('yojnabuddy.db')
    conn.row_factory = sqlite3.Row
    return conn

# Helper function to convert row to dict
def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {key: row[key] for key in row.keys()}

@app.route('/api/schemes', methods=['GET'])
def get_schemes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get query parameters
        category = request.args.get('category')
        state = request.args.get('state')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit

        # Base query
        query = """
            SELECT s.*, 
                   GROUP_CONCAT(DISTINCT c.name) as categories,
                   GROUP_CONCAT(DISTINCT rd.document) as required_documents,
                   GROUP_CONCAT(DISTINCT f.question || '|' || f.answer) as faqs
            FROM schemes s
            LEFT JOIN categories c ON s.category_id = c.id
            LEFT JOIN required_documents rd ON s.id = rd.scheme_id
            LEFT JOIN faqs f ON s.id = f.scheme_id
        """
        
        # Build WHERE clause
        conditions = []
        params = []
        
        if category:
            conditions.append("c.name = ?")
            params.append(category)
        
        if state:
            conditions.append("s.state = ?")
            params.append(state)
        
        if search:
            conditions.append("(s.name LIKE ? OR s.description LIKE ?)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " GROUP BY s.id"
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        # Execute query
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Process results
        schemes = []
        for row in rows:
            scheme = row_to_dict(row)
            
            # Process categories
            scheme['categories'] = scheme['categories'].split(',') if scheme['categories'] else []
            
            # Process required documents
            scheme['required_documents'] = scheme['required_documents'].split(',') if scheme['required_documents'] else []
            
            # Process FAQs
            faqs_processed = []
            if scheme['faqs']:
                for faq_item in scheme['faqs'].split(','):
                    if '|' in faq_item:
                        question, answer = faq_item.split('|', 1)
                        faqs_processed.append({'question': question, 'answer': answer})
                    # else: you could log a warning here if needed
            scheme['faqs'] = faqs_processed
            
            schemes.append(scheme)

        conn.close()
        return jsonify(schemes)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/schemes/<int:scheme_id>', methods=['GET'])
def get_scheme(scheme_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get scheme details
        cursor.execute("""
            SELECT s.*, 
                   GROUP_CONCAT(DISTINCT c.name) as categories,
                   GROUP_CONCAT(DISTINCT rd.document) as required_documents,
                   GROUP_CONCAT(DISTINCT f.question || '|' || f.answer) as faqs,
                   GROUP_CONCAT(DISTINCT t.name) as tags
            FROM schemes s
            LEFT JOIN categories c ON s.category_id = c.id
            LEFT JOIN required_documents rd ON s.id = rd.scheme_id
            LEFT JOIN faqs f ON s.id = f.scheme_id
            LEFT JOIN scheme_tags st ON s.id = st.scheme_id
            LEFT JOIN tags t ON st.tag_id = t.id
            WHERE s.id = ?
            GROUP BY s.id
        """, (scheme_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'Scheme not found'}), 404

        scheme = row_to_dict(row)
        
        # Process categories
        scheme['categories'] = scheme['categories'].split(',') if scheme['categories'] else []
        
        # Process required documents
        scheme['required_documents'] = scheme['required_documents'].split(',') if scheme['required_documents'] else []
        
        # Process FAQs
        faqs_processed = []
        if scheme['faqs']:
            for faq_item in scheme['faqs'].split(','):
                if '|' in faq_item:
                    question, answer = faq_item.split('|', 1)
                    faqs_processed.append({'question': question, 'answer': answer})
        scheme['faqs'] = faqs_processed
        scheme['tags'] = scheme['tags'].split(',') if scheme['tags'] else []

        conn.close()
        return jsonify(scheme)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT c.id, c.name, c.description, c.icon, c.color, COUNT(s.id) as scheme_count
            FROM categories c
            LEFT JOIN schemes s ON c.id = s.category_id
            GROUP BY c.id, c.name, c.description, c.icon, c.color
            ORDER BY scheme_count DESC
        ''')
        categories = [row_to_dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/states', methods=['GET'])
def get_states():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT state
            FROM schemes
            WHERE state IS NOT NULL
            ORDER BY state
        """)
        
        states = [row['state'] for row in cursor.fetchall()]
        conn.close()
        return jsonify(states)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/schemes/search', methods=['GET'])
def search_schemes():
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify([])

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT s.*, 
                   GROUP_CONCAT(DISTINCT c.name) as categories,
                   GROUP_CONCAT(DISTINCT rd.document) as required_documents,
                   GROUP_CONCAT(DISTINCT f.question || '|' || f.answer) as faqs
            FROM schemes s
            LEFT JOIN categories c ON s.category_id = c.id
            LEFT JOIN required_documents rd ON s.id = rd.scheme_id
            LEFT JOIN faqs f ON s.id = f.scheme_id
            WHERE s.name LIKE ? OR s.description LIKE ?
            GROUP BY s.id
        """, (f'%{query}%', f'%{query}%'))
        
        rows = cursor.fetchall()
        schemes = []
        
        for row in rows:
            scheme = row_to_dict(row)
            
            # Process categories
            scheme['categories'] = scheme['categories'].split(',') if scheme['categories'] else []
            
            # Process required documents
            scheme['required_documents'] = scheme['required_documents'].split(',') if scheme['required_documents'] else []
            
            # Process FAQs
            faqs_processed = []
            if scheme['faqs']:
                for faq_item in scheme['faqs'].split(','):
                    if '|' in faq_item:
                        question, answer = faq_item.split('|', 1)
                        faqs_processed.append({'question': question, 'answer': answer})
                    # else: you could log a warning here if needed
            scheme['faqs'] = faqs_processed
            
            schemes.append(scheme)

        conn.close()
        return jsonify(schemes)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/schemes/category/<int:category_id>', methods=['GET'])
def get_schemes_by_category_id(category_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get query parameters for pagination and sorting
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        sort_by = request.args.get('sortBy', 'relevance') # Corrected from sortby to sortBy

        # Validate parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100: # Max limit 100
            limit = 10
        
        valid_sort_options = ['relevance', 'newest', 'alphabetical']
        if sort_by not in valid_sort_options:
            sort_by = 'relevance'
            
        offset = (page - 1) * limit

        # Base query
        query_select = """
            SELECT s.*, 
                   GROUP_CONCAT(DISTINCT c.name) as categories,
                   GROUP_CONCAT(DISTINCT rd.document) as required_documents,
                   GROUP_CONCAT(DISTINCT f.question || '|' || f.answer) as faqs,
                   GROUP_CONCAT(DISTINCT t.name) as tags
            FROM schemes s
            LEFT JOIN categories c ON s.category_id = c.id
            LEFT JOIN required_documents rd ON s.id = rd.scheme_id
            LEFT JOIN faqs f ON s.id = f.scheme_id
            LEFT JOIN scheme_tags st ON s.id = st.scheme_id
            LEFT JOIN tags t ON st.tag_id = t.id
            WHERE s.category_id = ?
            GROUP BY s.id
        """
        
        # Sorting logic
        if sort_by == 'newest':
            query_select += " ORDER BY s.id DESC" # Assuming higher ID is newer
        elif sort_by == 'alphabetical':
            query_select += " ORDER BY s.name ASC"
        # For 'relevance', no specific order is applied here, or you might define a default.
            
        query_select += " LIMIT ? OFFSET ?"
        
        params = [category_id, limit, offset]

        cursor.execute(query_select, params)
        rows = cursor.fetchall()

        schemes = []
        for row in rows:
            scheme = row_to_dict(row)
            scheme['categories'] = scheme['categories'].split(',') if scheme['categories'] else []
            scheme['required_documents'] = scheme['required_documents'].split(',') if scheme['required_documents'] else []
            faqs_processed = []
            if scheme['faqs']:
                for faq_item in scheme['faqs'].split(','):
                    if '|' in faq_item:
                        question, answer = faq_item.split('|', 1)
                        faqs_processed.append({'question': question, 'answer': answer})
                    # else: you could log a warning here if needed
            scheme['faqs'] = faqs_processed
            scheme['tags'] = scheme['tags'].split(',') if scheme['tags'] else []
            schemes.append(scheme)

        # Get total count for pagination
        cursor.execute("SELECT COUNT(id) FROM schemes WHERE category_id = ?", (category_id,))
        total_schemes = cursor.fetchone()[0]
        
        conn.close()
        return jsonify({
            "data": schemes,
            "total": total_schemes,
            "page": page,
            "limit": limit,
            "totalPages": (total_schemes + limit - 1) // limit # Calculate total pages
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/schemes/category/<int:category_id>/<string:scheme_type>', methods=['GET'])
def get_schemes_by_category_and_type(category_id: int, scheme_type: str):
    try:
        if scheme_type not in ['state', 'central']:
            return jsonify({"error": "Invalid type. Must be 'state' or 'central'"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        # sort_by is not used by the frontend for this specific call, but good to be aware of
        # sort_by = request.args.get('sortBy', 'relevance') 

        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        
        offset = (page - 1) * limit

        query_select = """
            SELECT s.*,
                   GROUP_CONCAT(DISTINCT c.name) as categories,
                   GROUP_CONCAT(DISTINCT rd.document) as required_documents,
                   GROUP_CONCAT(DISTINCT f.question || '|' || f.answer) as faqs,
                   GROUP_CONCAT(DISTINCT t.name) as tags
            FROM schemes s
            LEFT JOIN categories c ON s.category_id = c.id
            LEFT JOIN required_documents rd ON s.id = rd.scheme_id
            LEFT JOIN faqs f ON s.id = f.scheme_id
            LEFT JOIN scheme_tags st ON s.id = st.scheme_id
            LEFT JOIN tags t ON st.tag_id = t.id
            WHERE s.category_id = ? AND s.scheme_type = ?
            GROUP BY s.id
            LIMIT ? OFFSET ?
        """
        # Add sorting if needed in the future, e.g.
        # if sort_by == 'newest':
        #     query_select += " ORDER BY s.id DESC" 
        # elif sort_by == 'alphabetical':
        #     query_select += " ORDER BY s.name ASC"

        params = [category_id, scheme_type, limit, offset]
        cursor.execute(query_select, params)
        rows = cursor.fetchall()

        schemes = []
        for row in rows:
            scheme = row_to_dict(row)
            scheme['categories'] = scheme['categories'].split(',') if scheme['categories'] else []
            scheme['required_documents'] = scheme['required_documents'].split(',') if scheme['required_documents'] else []
            faqs_processed = []
            if scheme['faqs']:
                for faq_item in scheme['faqs'].split(','):
                    if '|' in faq_item:
                        question, answer = faq_item.split('|', 1)
                        faqs_processed.append({'question': question, 'answer': answer})
                    # else: you could log a warning here if needed
            scheme['faqs'] = faqs_processed
            scheme['tags'] = scheme['tags'].split(',') if scheme['tags'] else []
            schemes.append(scheme)

        cursor.execute("SELECT COUNT(id) FROM schemes WHERE category_id = ? AND scheme_type = ?", (category_id, scheme_type))
        total_schemes = cursor.fetchone()[0]
        
        conn.close()
        return jsonify({
            "data": schemes,
            "total": total_schemes,
            "page": page,
            "limit": limit,
            "totalPages": (total_schemes + limit - 1) // limit
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Register routes from api.py
app.register_blueprint(my_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 