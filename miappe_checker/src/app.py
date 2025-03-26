from flask import Flask, render_template, request, jsonify
import os
import sys
import logging
from src.models.miappe_schema import MIAPPESchema
from datetime import datetime
import psycopg2
from psycopg2.extras import Json

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Load MIAPPE schema
schema = MIAPPESchema()

# Database connection
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'miappe'),
        user=os.getenv('POSTGRES_USER', 'miappe_user'),
        password=os.getenv('POSTGRES_PASSWORD', 'miappe_password'),
        host=os.getenv('POSTGRES_HOST', 'miappe-postgres'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )

@app.route('/')
def index():
    return render_template('index.html', schema=schema)

@app.route('/miappe/save_checklist', methods=['POST'])
def save_checklist():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        app.logger.info(f"Received data: {data}")

        # Validate fields and determine completion status
        missing_fields = []
        incomplete_scopes = []
        
        for scope_name, scope_data in data.items():
            if scope_name not in schema.scopes:
                continue
                
            scope = schema.scopes[scope_name]
            
            # Check mandatory scopes (requirement == 0)
            if scope.requirement == 0:
                if not scope_data or not any(scope_data.values()):
                    missing_fields.append(scope_name)
                    incomplete_scopes.append(scope_name)
            # Check recommended scopes (requirement == 1)
            elif scope.requirement == 1:
                if scope_data and any(scope_data.values()):
                    # If any field in a recommended scope is filled, all mandatory fields must be filled
                    mandatory_fields = schema.get_mandatory_fields(scope_name)
                    for field in mandatory_fields:
                        if field not in scope_data or not scope_data[field].strip():
                            incomplete_scopes.append(scope_name)
                            break

        # Determine overall form status
        is_complete = len(incomplete_scopes) == 0

        app.logger.info(f"Validation results - is_complete: {is_complete}, incomplete_scopes: {incomplete_scopes}")

        # Store the data in PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # Insert into miappe_checklists table
            cur.execute("""
                INSERT INTO miappe_checklists 
                (data, is_complete, incomplete_scopes, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                Json(data),
                is_complete,
                Json(incomplete_scopes),
                datetime.utcnow(),
                datetime.utcnow()
            ))
            
            checklist_id = cur.fetchone()[0]
            conn.commit()

            response_data = {
                'success': True,
                'message': 'Checklist saved successfully',
                'checklist_id': checklist_id,
                'is_complete': is_complete,
                'incomplete_scopes': incomplete_scopes,
                'missing_fields': missing_fields
            }
            app.logger.info(f"Sending response: {response_data}")
            return jsonify(response_data), 200

        except Exception as e:
            conn.rollback()
            app.logger.error(f"Database error: {str(e)}")
            return jsonify({'error': f"Database error: {str(e)}"}), 500
        finally:
            cur.close()
            conn.close()

    except Exception as e:
        app.logger.error(f"Error saving checklist: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Use port from environment variable or default to 80
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port) 