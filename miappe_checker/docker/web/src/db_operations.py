"""
Database operations for MIAPPE metadata checker.
This file contains all database-related operations using consistent naming conventions.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
import logging
from .field_mappings import DB_TO_BACKEND, BACKEND_TO_FRONTEND

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host="miappe-postgres",
            database="miappe",
            user="miappe_user",
            password="miappe_password",
            cursor_factory=RealDictCursor
        )
        logger.info("Successfully connected to database")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise

def create_new_investigation(cursor, investigation_id):
    """Create a new investigation record."""
    try:
        cursor.execute("""
            INSERT INTO INVESTIGATION (
                INVESTIGATION_ID, INVESTIGATION_ID_BINDING,
                TITLE, TITLE_BINDING,
                DESCRIPTION, DESCRIPTION_BINDING,
                SUBMISSION_DATE, SUBMISSION_DATE_BINDING,
                PUBLIC_RELEASE_DATE, PUBLIC_RELEASE_DATE_BINDING,
                LICENSE, LICENSE_BINDING,
                MIAPPE_VERSION, MIAPPE_VERSION_BINDING,
                ASSOCIATED_PUBLICATION, ASSOCIATED_PUBLICATION_BINDING
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id, INVESTIGATION_ID, INVESTIGATION_ID_BINDING, TITLE, TITLE_BINDING, 
                      DESCRIPTION, DESCRIPTION_BINDING, SUBMISSION_DATE, SUBMISSION_DATE_BINDING,
                      PUBLIC_RELEASE_DATE, PUBLIC_RELEASE_DATE_BINDING, LICENSE, LICENSE_BINDING,
                      MIAPPE_VERSION, MIAPPE_VERSION_BINDING, ASSOCIATED_PUBLICATION, ASSOCIATED_PUBLICATION_BINDING
        """, (
            investigation_id, None,
            f"Investigation {investigation_id}", None,
            "", None,
            None, None,
            None, None,
            None, None,
            "1.0", None,
            "", None
        ))
        result = cursor.fetchone()
        logger.info(f"Created new investigation: {result}")
        return result
    except Exception as e:
        logger.error(f"Error creating investigation: {str(e)}")
        raise

def create_new_study(cursor, investigation_id, study_id):
    """Create a new study record."""
    try:
        cursor.execute("""
            INSERT INTO STUDY (
                INVESTIGATION_ID, STUDY_ID, STUDY_TITLE, STUDY_DESCRIPTION,
                STUDY_START_DATE, STUDY_END_DATE, CONTACT_INSTITUTION,
                LOCATION_COUNTRY, SITE_NAME, LOCATION_LATITUDE,
                LOCATION_LONGITUDE, LOCATION_ALTITUDE,
                EXPERIMENTAL_DESIGN_DESCRIPTION, EXPERIMENTAL_DESIGN_TYPE,
                OBSERVATION_UNIT_LEVEL_HIERARCHY, OBSERVATION_UNIT_DESCRIPTION,
                GROWTH_FACILITY_DESCRIPTION, GROWTH_FACILITY_TYPE,
                CULTURAL_PRACTICES, EXPERIMENTAL_DESIGN_MAP
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id, STUDY_ID, STUDY_TITLE, STUDY_DESCRIPTION
        """, (
            investigation_id,
            study_id,
            f"Study {study_id}",
            "",
            datetime.now(timezone.utc),
            None,
            "Not specified",
            "XX",
            "Not specified",
            None,
            None,
            None,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            []
        ))
        result = cursor.fetchone()
        logger.info(f"Created new study: {result}")
        return result
    except Exception as e:
        logger.error(f"Error creating study: {str(e)}")
        raise

def get_study_data(cursor, study_db_id, investigation_db_id):
    """Get all data for a study, including related records."""
    try:
        # Get investigation data
        cursor.execute("""
            SELECT * FROM INVESTIGATION WHERE id = %s
        """, (investigation_db_id,))
        investigation = cursor.fetchone()
        
        # Get study data
        cursor.execute("""
            SELECT * FROM STUDY WHERE id = %s
        """, (study_db_id,))
        study = cursor.fetchone()
        
        # Get related records
        related_tables = [
            'PERSON',
            'DATA_FILE',
            'BIOLOGICAL_MATERIAL',
            'ENVIRONMENT',
            'EXPERIMENTAL_FACTOR',
            'EVENT',
            'OBSERVATION_UNIT',
            'SAMPLE',
            'OBSERVED_VARIABLE'
        ]
        
        result = {
            'investigation': investigation,
            'study': study
        }
        
        for table in related_tables:
            cursor.execute(f"""
                SELECT * FROM {table} WHERE study_id = %s
            """, (study_db_id,))
            records = cursor.fetchall()
            if records:
                result[table.lower()] = records[0] if len(records) == 1 else records
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting study data: {str(e)}")
        raise

def convert_db_to_frontend(data):
    """Convert database field names to frontend field names."""
    if not data:
        return None
        
    result = {}
    for db_field, value in data.items():
        if db_field in DB_TO_BACKEND:
            backend_field = DB_TO_BACKEND[db_field]
            if backend_field in BACKEND_TO_FRONTEND:
                frontend_field = BACKEND_TO_FRONTEND[backend_field]
                result[frontend_field] = value
            else:
                result[backend_field] = value
        else:
            result[db_field] = value
    return result

def convert_frontend_to_db(data):
    """Convert frontend field names to database field names."""
    if not data:
        return None
        
    result = {}
    # Process each scope
    for scope, scope_data in data.items():
        if not isinstance(scope_data, dict):
            continue
            
        result[scope] = {}
        for field, value in scope_data.items():
            # Convert camelCase to UPPER_SNAKE_CASE
            db_field = ''.join(['_' + c.upper() if c.isupper() else c.upper() for c in field]).lstrip('_')
            result[scope][db_field] = value
            
    return result 