"""
Main Flask application for MIAPPE metadata checker.
This file contains the core application logic and API endpoints.
"""

from flask import Flask, request, jsonify, render_template, url_for
from datetime import datetime, timezone
import psycopg2
from psycopg2.extras import RealDictCursor
from src.field_mappings import DB_TO_BACKEND, BACKEND_TO_FRONTEND
from src.db_operations import (
    get_db_connection,
    create_new_investigation,
    create_new_study,
    get_study_data,
    convert_db_to_frontend,
    convert_frontend_to_db
)

app = Flask(__name__, static_url_path='/miappe/static', static_folder='static')

@app.route('/miappe/')
def index():
    """Render the main application page."""
    return render_template('index.html')

@app.route('/miappe/api/check_investigation', methods=['POST'])
def check_investigation():
    """Check if an investigation exists and create it if it doesn't."""
    try:
        data = request.get_json()
        investigation_id = data.get('investigation_id')
        study_id = data.get('study_id')
        
        if not investigation_id or not study_id:
            return jsonify({'error': 'Missing investigation_id or study_id'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if investigation exists
        cursor.execute("""
            SELECT id FROM INVESTIGATION 
            WHERE investigation_id = %s
        """, (investigation_id,))
        
        result = cursor.fetchone()
        
        if not result:
            # Create new investigation
            investigation_db_id = create_new_investigation(cursor, investigation_id)
            conn.commit()
        else:
            investigation_db_id = result['id']
        
        # Check if study exists
        cursor.execute("""
            SELECT id FROM STUDY 
            WHERE study_id = %s AND investigation_db_id = %s
        """, (study_id, investigation_db_id))
        
        result = cursor.fetchone()
        
        if not result:
            # Create new study
            study_db_id = create_new_study(cursor, investigation_db_id, study_id)
            conn.commit()
        else:
            study_db_id = result['id']
        
        # Get study data
        study_data = get_study_data(cursor, study_id, investigation_db_id)
        
        # Convert field names for frontend
        frontend_data = convert_db_to_frontend(study_data)
        
        cursor.close()
        conn.close()
        
        return jsonify(frontend_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/miappe/api/save_checklist', methods=['POST'])
def save_checklist():
    """Save the checklist data for a study."""
    try:
        data = request.get_json()
        investigation_id = data.get('investigation_id')
        study_id = data.get('study_id')
        form_data = data.get('data')
        
        if not all([investigation_id, study_id, form_data]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get investigation and study IDs
        cursor.execute("""
            SELECT i.id as investigation_db_id, s.id as study_db_id
            FROM INVESTIGATION i
            JOIN STUDY s ON s.investigation_db_id = i.id
            WHERE i.investigation_id = %s AND s.study_id = %s
        """, (investigation_id, study_id))
        
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'Investigation or study not found'}), 404
        
        investigation_db_id = result['investigation_db_id']
        study_db_id = result['study_db_id']
        
        # Convert frontend field names to database field names
        db_data = convert_frontend_to_db(form_data)
        
        # Update study data
        update_fields = []
        update_values = []
        
        for field, value in db_data.items():
            if field in DB_TO_BACKEND:
                update_fields.append(f"{DB_TO_BACKEND[field]} = %s")
                update_values.append(value)
        
        if update_fields:
            update_values.append(study_db_id)
            update_values.append(investigation_db_id)
            
            query = f"""
                UPDATE STUDY 
                SET {', '.join(update_fields)}, last_updated = %s
                WHERE id = %s AND investigation_db_id = %s
            """
            
            cursor.execute(query, update_values + [datetime.now(timezone.utc)])
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Checklist saved successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 