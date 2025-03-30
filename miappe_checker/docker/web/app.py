"""
Main Flask application for MIAPPE metadata checker.
This file contains the core application logic and API endpoints.

NOTE: Rewrite get_mongo_fields if you want to use a different database or path to the mongo database.
"""

from flask import Flask, request, jsonify, render_template, url_for
from datetime import datetime, timezone
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from pymongo import MongoClient
from src.field_mappings import (
    DB_TO_BACKEND, 
    BACKEND_TO_FRONTEND,
    FRONTEND_TO_BACKEND
)
from src.db_operations import (
    get_db_connection,
    create_new_investigation,
    create_new_study,
    get_study_data,
    convert_db_to_frontend,
    convert_frontend_to_db
)
from src.models.miappe_schema import MIAPPESchema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_url_path='/miappe/static', static_folder='static')

# Initialize MIAPPE schema
schema = MIAPPESchema()
schema.load_from_csv("/app/src/models/MIAPPE_Checklist_Data_Model_with_Requirements.csv")

def get_mongo_fields():
    """Get fields from MongoDB plant_data collection."""
    client = None
    try:
        app.logger.info("Attempting to connect to MongoDB...")
        client = MongoClient('mongodb://mongodb-service:27017/plant_data', serverSelectionTimeoutMS=5000)
        # Test the connection
        client.server_info()
        app.logger.info("Successfully connected to MongoDB")
        
        db = client.plant_data
        collection = db.plant_data
        
        # Get a sample document to extract fields
        app.logger.info("Fetching sample document from plant_data collection...")
        sample = collection.find_one()
        if not sample:
            app.logger.warning("No documents found in plant_data collection")
            return []
        
        def get_nested_fields(doc, prefix=''):
            fields = []
            for key, value in doc.items():
                if key.startswith('_'):
                    continue
                field = f"{prefix}{key}" if prefix else key
                fields.append(field)
                if isinstance(value, dict):
                    fields.extend(get_nested_fields(value, f"{field}."))
            return fields
        
        # Get all field names from the document, including nested fields
        fields = get_nested_fields(sample)
        app.logger.info(f"Found {len(fields)} fields in plant_data collection")
        
        return sorted(fields)
    except Exception as e:
        app.logger.error(f"Error getting MongoDB fields: {str(e)}")
        app.logger.error(f"Error type: {type(e).__name__}")
        return []
    finally:
        if client:
            try:
                client.close()
                app.logger.info("MongoDB connection closed")
            except Exception as e:
                app.logger.error(f"Error closing MongoDB connection: {str(e)}")

@app.route('/miappe/')
def index():
    """Render the main application page."""
    mongo_fields = get_mongo_fields()
    return render_template('index.html', scopes=schema.scopes, mongo_fields=mongo_fields)

@app.route('/miappe/api/check_investigation', methods=['POST'])
def check_investigation():
    """Check if an investigation exists and create it if it doesn't."""
    try:
        data = request.get_json()
        logger.info(f"Received request data: {data}")
        
        investigation_id = data.get('investigation_id')
        study_id = data.get('study_id')
        
        if not investigation_id or not study_id:
            return jsonify({'error': 'Missing investigation_id or study_id'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Check if investigation exists
            cursor.execute("""
                SELECT id, created_at, updated_at FROM INVESTIGATION 
                WHERE INVESTIGATION_ID = %s
            """, (investigation_id,))
            
            result = cursor.fetchone()
            logger.info(f"Investigation query result: {result}")
            
            is_new_record = False
            if not result:
                # Create new investigation
                result = create_new_investigation(cursor, investigation_id)
                logger.info(f"Created new investigation: {result}")
                conn.commit()
                investigation_db_id = result['id']
                is_new_record = True
            else:
                investigation_db_id = result['id']
            
            # Check if study exists
            cursor.execute("""
                SELECT id, created_at, updated_at FROM STUDY 
                WHERE STUDY_ID = %s AND INVESTIGATION_ID = %s
            """, (study_id, investigation_db_id))
            
            result = cursor.fetchone()
            logger.info(f"Study query result: {result}")
            
            if not result:
                # Create new study
                result = create_new_study(cursor, investigation_db_id, study_id)
                logger.info(f"Created new study: {result}")
                conn.commit()
                study_db_id = result['id']
                is_new_record = True
            else:
                study_db_id = result['id']
                
            # Get study data using the UUID IDs
            study_data = get_study_data(cursor, study_db_id, investigation_db_id)
            logger.info(f"Retrieved study data: {study_data}")
            
            # Convert field names for frontend
            frontend_data = convert_db_to_frontend(study_data)
            
            # Add metadata about record status
            frontend_data['is_new_record'] = is_new_record
            if not is_new_record and result:
                frontend_data['created_at'] = result['created_at'].isoformat()
                frontend_data['updated_at'] = result['updated_at'].isoformat()
            
            cursor.close()
            conn.close()
            
            return jsonify(frontend_data)
            
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            if conn:
                conn.rollback()
            raise
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
    except Exception as e:
        logger.error(f"Error in check_investigation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/miappe/api/save_checklist', methods=['POST'])
def save_checklist():
    """Save checklist data for a study"""
    try:
        data = request.get_json()
        app.logger.info(f"Received request data: {data}")
        
        if not data or 'investigation_id' not in data or 'study_id' not in data or 'form_data' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        # Get database IDs
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get investigation database ID
        cursor.execute("""
            SELECT id, created_at FROM INVESTIGATION 
            WHERE INVESTIGATION_ID = %s
        """, (data['investigation_id'],))
        investigation_result = cursor.fetchone()
        if not investigation_result:
            return jsonify({'error': 'Investigation not found'}), 404
        investigation_db_id = investigation_result['id']
        investigation_created_at = investigation_result['created_at']
        app.logger.info(f"Found investigation with ID: {investigation_db_id}")
        
        # Get study database ID
        cursor.execute("""
            SELECT id, created_at FROM STUDY 
            WHERE STUDY_ID = %s
        """, (data['study_id'],))
        study_result = cursor.fetchone()
        if not study_result:
            return jsonify({'error': 'Study not found'}), 404
        study_db_id = study_result['id']
        study_created_at = study_result['created_at']
        app.logger.info(f"Found study with ID: {study_db_id}")

        # Convert frontend data to database format
        form_data = data['form_data']
        app.logger.info(f"Form data to process: {form_data}")

        # Process each scope
        for scope, fields in form_data.items():
            if not fields:  # Skip empty scopes
                continue
                
            # Convert scope name to table name (handle spaces)
            table_name = scope.replace(' ', '_').upper()
            app.logger.info(f"Processing scope: {scope} for table: {table_name}")
            
            # Build update fields and values
            update_fields = []
            update_values = []
            
            # Track processed fields to avoid duplicates
            processed_fields = set()
            
            for field, value in fields.items():
                # Skip metadata fields
                if field in ['is_new_record', 'created_at']:
                    continue
                    
                # Convert frontend field to backend field
                backend_field = FRONTEND_TO_BACKEND.get(field)
                if not backend_field:
                    app.logger.warning(f"No backend mapping found for field: {field}")
                    continue
                    
                # Get database field from backend field
                db_field = None
                for db_key, backend_value in DB_TO_BACKEND.items():
                    if backend_value == backend_field:
                        db_field = db_key.split('.')[1]  # Get the part after the scope
                        break
                        
                if not db_field:
                    app.logger.warning(f"No database mapping found for backend field: {backend_field}")
                    continue
                    
                # Check if this is a binding field
                is_binding = field.endswith('_binding')
                if is_binding:
                    field = field[:-8]  # Remove '_binding' suffix
                    db_field = f"{db_field}_BINDING"
                    app.logger.info(f"Processing binding field: {field} -> {db_field} with value: {value}")
                else:
                    app.logger.info(f"Processing regular field: {field} -> {db_field} with value: {value}")
                
                # Skip if we've already processed this field
                if field in processed_fields:
                    continue
                processed_fields.add(field)
                
                # Convert empty string to None for database
                if value == '':
                    value = None
                
                update_fields.append(f"{db_field} = %s")
                update_values.append(value)
        
            if not update_fields:  # Skip if no fields to update
                app.logger.info(f"No fields to update for scope {scope}")
                continue
                
            # Add updated_at timestamp
            update_fields.append("updated_at = %s")
            update_values.append(datetime.now(timezone.utc))
            
            # Build and execute update query
            update_query = f"""
                UPDATE {table_name}
                SET {', '.join(update_fields)}
                WHERE {'id' if scope == 'INVESTIGATION' else 'study_id'} = %s
            """
            update_values.append(investigation_db_id if scope == 'INVESTIGATION' else study_db_id)
            
            app.logger.info(f"Update query for {scope}: \n{update_query}")
            app.logger.info(f"Update values for {scope}: {update_values}")
            
            try:
                cursor.execute(update_query, update_values)
                app.logger.info(f"Update affected {cursor.rowcount} rows")
                
                if cursor.rowcount == 0 and scope not in ['INVESTIGATION', 'STUDY']:
                    app.logger.info(f"No rows updated for {scope}, attempting insert")
                    # For non-INVESTIGATION/STUDY tables, try to insert if update fails
                    insert_fields = []
                    insert_values = []
                    
                    for field, value in fields.items():
                        backend_field = FRONTEND_TO_BACKEND.get(field)
                        if backend_field:
                            for db_key, backend_value in DB_TO_BACKEND.items():
                                if backend_value == backend_field:
                                    db_field = db_key.split('.')[1]
                                    # Check if this is a binding field
                                    is_binding = field.endswith('_binding')
                                    if is_binding:
                                        field = field[:-8]  # Remove '_binding' suffix
                                        db_field = f"{db_field}_BINDING"
                                        app.logger.info(f"Processing binding field for insert: {field} -> {db_field} with value: {value}")
                                    else:
                                        app.logger.info(f"Processing regular field for insert: {field} -> {db_field} with value: {value}")
                                    
                                    # Convert empty string to None for database
                                    if value == '':
                                        value = None
                                        
                                    insert_fields.append(db_field)
                                    insert_values.append(value)
                                    break
                    
                    insert_fields.append('study_id')
                    insert_values.append(study_db_id)
                    
                    insert_query = f"""
                        INSERT INTO {table_name} ({', '.join(insert_fields)})
                        VALUES ({', '.join(['%s'] * len(insert_values))})
                    """
                    app.logger.info(f"Insert query for {scope}: \n{insert_query}")
                    app.logger.info(f"Insert values for {scope}: {insert_values}")
                    
                    cursor.execute(insert_query, insert_values)
                    app.logger.info(f"Insert successful for {scope}")
            except Exception as e:
                app.logger.error(f"Error updating {scope}: {str(e)}")
                app.logger.error(f"Query: {update_query}")
                app.logger.error(f"Values: {update_values}")
                conn.rollback()
                return jsonify({'error': f'Error updating {scope}: {str(e)}'}), 500

        # Commit transaction
        conn.commit()
        app.logger.info("Transaction committed successfully")
        return jsonify({'message': 'Checklist saved successfully'}), 200

    except Exception as e:
        app.logger.error(f"Error in save_checklist: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 