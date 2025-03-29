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
            INSERT INTO INVESTIGATION (INVESTIGATION_ID, TITLE, DESCRIPTION, MIAPPE_VERSION)
            VALUES (%s, %s, %s, %s)
            RETURNING id, INVESTIGATION_ID, TITLE, DESCRIPTION, MIAPPE_VERSION
        """, (investigation_id, f"Investigation {investigation_id}", "", "1.0"))
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
    """Get study data with all related information."""
    try:
        # Get investigation data
        cursor.execute("""
            SELECT 
                INVESTIGATION_ID,
                TITLE,
                DESCRIPTION,
                SUBMISSION_DATE,
                PUBLIC_RELEASE_DATE,
                LICENSE,
                MIAPPE_VERSION,
                ASSOCIATED_PUBLICATION
            FROM INVESTIGATION 
            WHERE id = %s
        """, (investigation_db_id,))
        investigation = cursor.fetchone()
        
        # Get study data
        cursor.execute("""
            SELECT 
                STUDY_ID,
                STUDY_TITLE,
                STUDY_DESCRIPTION,
                STUDY_START_DATE,
                STUDY_END_DATE,
                CONTACT_INSTITUTION,
                LOCATION_COUNTRY,
                SITE_NAME,
                LOCATION_LATITUDE,
                LOCATION_LONGITUDE,
                LOCATION_ALTITUDE,
                EXPERIMENTAL_DESIGN_DESCRIPTION,
                EXPERIMENTAL_DESIGN_TYPE,
                OBSERVATION_UNIT_LEVEL_HIERARCHY,
                OBSERVATION_UNIT_DESCRIPTION,
                GROWTH_FACILITY_DESCRIPTION,
                GROWTH_FACILITY_TYPE,
                CULTURAL_PRACTICES,
                EXPERIMENTAL_DESIGN_MAP
            FROM STUDY 
            WHERE id = %s
        """, (study_db_id,))
        study = cursor.fetchone()
        
        # Get person data
        cursor.execute("""
            SELECT 
                NAME,
                EMAIL,
                PERSON_ID,
                ROLE,
                AFFILIATION
            FROM PERSON 
            WHERE STUDY_ID = %s
        """, (study_db_id,))
        person = cursor.fetchone() or {}
        
        # Get data file data
        cursor.execute("""
            SELECT 
                FILE_LINK,
                DESCRIPTION,
                VERSION
            FROM DATA_FILE 
            WHERE STUDY_ID = %s
        """, (study_db_id,))
        data_file = cursor.fetchone() or {}
        
        # Get biological material data
        cursor.execute("""
            SELECT 
                BIOLOGICAL_MATERIAL_ID,
                EXTERNAL_ID,
                ORGANISM,
                GENUS,
                SPECIES,
                INFRASPECIFIC_NAME,
                LATITUDE,
                LONGITUDE,
                ALTITUDE,
                COORDINATE_UNCERTAINTY,
                PREPROCESSING,
                SOURCE_ID,
                SOURCE_DOI,
                SOURCE_ACCESSION_NUMBER,
                SOURCE_ACCESSION_NAME,
                SOURCE_INSTITUTION_CODE,
                SOURCE_INSTITUTION_NAME,
                SOURCE_OTHER_IDS,
                SOURCE_LATITUDE,
                SOURCE_LONGITUDE,
                SOURCE_ALTITUDE,
                SOURCE_COORDINATE_UNCERTAINTY,
                SOURCE_DESCRIPTION
            FROM BIOLOGICAL_MATERIAL 
            WHERE STUDY_ID = %s
        """, (study_db_id,))
        biological_material = cursor.fetchone() or {}
        
        # Get environment data
        cursor.execute("""
            SELECT 
                PARAMETER,
                PARAMETER_VALUE
            FROM ENVIRONMENT 
            WHERE STUDY_ID = %s
        """, (study_db_id,))
        environment = cursor.fetchone() or {}
        
        # Get experimental factor data
        cursor.execute("""
            SELECT 
                FACTOR_TYPE,
                FACTOR_DESCRIPTION,
                FACTOR_VALUES
            FROM EXPERIMENTAL_FACTOR 
            WHERE STUDY_ID = %s
        """, (study_db_id,))
        experimental_factor = cursor.fetchone() or {}
        
        # Get event data
        cursor.execute("""
            SELECT 
                EVENT_TYPE,
                ACCESSION_NUMBER,
                DESCRIPTION,
                EVENT_DATE
            FROM EVENT 
            WHERE STUDY_ID = %s
        """, (study_db_id,))
        event = cursor.fetchone() or {}
        
        # Get observation unit data
        cursor.execute("""
            SELECT 
                OBSERVATION_UNIT_ID,
                OBSERVATION_UNIT_TYPE,
                EXTERNAL_ID,
                SPATIAL_DISTRIBUTION,
                FACTOR_VALUES
            FROM OBSERVATION_UNIT 
            WHERE STUDY_ID = %s
        """, (study_db_id,))
        observation_unit = cursor.fetchone() or {}
        
        # Get sample data
        cursor.execute("""
            SELECT 
                SAMPLE_ID,
                DEVELOPMENT_STAGE,
                ANATOMICAL_ENTITY,
                DESCRIPTION,
                COLLECTION_DATE,
                EXTERNAL_ID
            FROM SAMPLE 
            WHERE STUDY_ID = %s
        """, (study_db_id,))
        sample = cursor.fetchone() or {}
        
        # Get observed variable data
        cursor.execute("""
            SELECT 
                VARIABLE_ID,
                VARIABLE_NAME,
                ACCESSION_NUMBER,
                TRAIT_NAME,
                TRAIT_ENTITY,
                TRAIT_ENTITY_ACCESSION_NUMBER,
                TRAIT_CHARACTERISTIC,
                TRAIT_CHARACTERISTIC_ACCESSION_NUMBER,
                TRAIT_ACCESSION_NUMBER,
                METHOD_NAME,
                METHOD_ACCESSION_NUMBER,
                METHOD_DESCRIPTION,
                METHOD_REFERENCE,
                SCALE_NAME,
                SCALE_ACCESSION_NUMBER,
                TIME_SCALE
            FROM OBSERVED_VARIABLE 
            WHERE STUDY_ID = %s
        """, (study_db_id,))
        observed_variable = cursor.fetchone() or {}
        
        # Structure the data by scope
        result = {
            'investigation': investigation,
            'study': study,
            'person': person,
            'data_file': data_file,
            'biological_material': biological_material,
            'environment': environment,
            'experimental_factor': experimental_factor,
            'event': event,
            'observation_unit': observation_unit,
            'sample': sample,
            'observed_variable': observed_variable
        }
        
        logger.info(f"Retrieved study data: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving study data: {str(e)}")
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