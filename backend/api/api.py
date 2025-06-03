import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from data_management.database import Database
import re
from my_blueprint import my_blueprint  # Replace with the actual module and blueprint name

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register the blueprint
app.register_blueprint(my_blueprint)

# Initialize database
db = Database()

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent SQL injection."""
    # Remove any SQL keywords
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'UNION', 'JOIN']
    text = text.upper()
    for keyword in sql_keywords:
        text = text.replace(keyword, '')
    return text

def validate_limit_offset(limit: int, offset: int) -> tuple:
    """Validate and sanitize limit and offset parameters."""
    try:
        limit = min(max(int(limit), 1), 100)  # Between 1 and 100
    except (ValueError, TypeError):
        limit = 10
    try:
        offset = max(int(offset), 0)  # Non-negative
    except (ValueError, TypeError):
        offset = 0
    return limit, offset

@app.route('/')
def root():
    """Welcome message."""
    return jsonify({
        "message": "Welcome to YojnaBuddy API",
        "version": "1.0.0",
        "endpoints": {
            "/categories": "Get all categories with scheme counts",
            "/schemes/category/:categoryId": "Get schemes by category",
            "/schemes/:id": "Get scheme details",
            "/schemes/category/:categoryId/:type": "Get schemes by type (state/central)"
        }
    })

@app.route('/categories')
def list_categories():
    """Get all categories with scheme counts."""
    try:
        categories = db.get_all_categories_with_counts()
        return jsonify(categories)
    except Exception as e:
        import traceback
        print("Error in /categories:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/schemes/category/<category_id>')
def get_schemes_by_category(category_id):
    """Get schemes by category with pagination and sorting."""
    try:
        # Get and validate query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        sort_by = request.args.get('sortBy', 'relevance')
        
        # Validate parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        if sort_by not in ['relevance', 'newest', 'alphabetical']:
            sort_by = 'relevance'
            
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get schemes
        schemes = db.get_schemes_by_category(
            category_id=category_id,
            limit=limit,
            offset=offset,
            sort_by=sort_by
        )
        
        # Get total count
        total = db.get_scheme_count_by_category(category_id)
        
        return jsonify({
            "data": schemes,
            "total": total
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/schemes/<scheme_id>')
def get_scheme_details(scheme_id):
    """Get detailed information about a specific scheme."""
    try:
        scheme = db.get_scheme_details(scheme_id)
        if not scheme:
            return jsonify({"error": "Scheme not found"}), 404
        return jsonify(scheme)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/schemes/category/<category_id>/<type>')
def get_schemes_by_type(category_id, type):
    """Get schemes by category and type (state/central) with pagination."""
    try:
        # Validate type
        if type not in ['state', 'central']:
            return jsonify({"error": "Invalid type. Must be 'state' or 'central'"}), 400
            
        # Get and validate query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Validate parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
            
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get schemes
        schemes = db.get_schemes_by_category_and_type(
            category_id=category_id,
            scheme_type=type,
            limit=limit,
            offset=offset
        )
        
        # Get total count
        total = db.get_scheme_count_by_category_and_type(category_id, type)
        
        return jsonify({
            "data": schemes,
            "total": total
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 