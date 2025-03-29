"""
Database operations for MIAPPE metadata checker.
This file contains all database-related operations using consistent naming conventions.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
from .field_mappings import DB_TO_BACKEND, BACKEND_TO_FRONTEND

def get_db_connection():
    """Get a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host="miappe-postgres",
        database="miappe",
        user="miappe_user",
        password="miappe123",
        cursor_factory=RealDictCursor
    )

def create_new_investigation(cursor, investigation_id):
    """Create a new investigation record."""
    cursor.execute("""
        INSERT INTO INVESTIGATION (INVESTIGATION_ID, TITLE, DESCRIPTION, MIAPPE_VERSION)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (investigation_id, f"Investigation {investigation_id}", "", "1.0"))
    return cursor.fetchone()

def create_new_study(cursor, investigation_db_id, study_id):
    """Create a new study record."""
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
        RETURNING id
    """, (
        investigation_db_id,
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
    return cursor.fetchone()

def get_study_data(cursor, study_id, investigation_db_id):
    """Get study data with all related information."""
    cursor.execute("""
        WITH study_data AS (
            SELECT s.*, i.TITLE as INVESTIGATION_TITLE
            FROM STUDY s
            JOIN INVESTIGATION i ON s.INVESTIGATION_ID = i.id
            WHERE s.STUDY_ID = %s AND s.INVESTIGATION_ID = %s
        )
        SELECT 
            s.id,
            s.STUDY_ID,
            s.STUDY_TITLE,
            s.STUDY_DESCRIPTION,
            s.STUDY_START_DATE,
            s.STUDY_END_DATE,
            s.CONTACT_INSTITUTION,
            s.LOCATION_COUNTRY,
            s.SITE_NAME,
            s.LOCATION_LATITUDE,
            s.LOCATION_LONGITUDE,
            s.LOCATION_ALTITUDE,
            s.EXPERIMENTAL_DESIGN_DESCRIPTION,
            s.EXPERIMENTAL_DESIGN_TYPE,
            s.OBSERVATION_UNIT_LEVEL_HIERARCHY,
            s.OBSERVATION_UNIT_DESCRIPTION,
            s.GROWTH_FACILITY_DESCRIPTION,
            s.GROWTH_FACILITY_TYPE,
            s.CULTURAL_PRACTICES,
            s.EXPERIMENTAL_DESIGN_MAP,
            s.INVESTIGATION_TITLE,
            json_agg(DISTINCT jsonb_build_object(
                'id', p.id,
                'name', p.NAME,
                'role', p.ROLE,
                'affiliation', p.AFFILIATION
            )) as PERSON,
            json_agg(DISTINCT jsonb_build_object(
                'id', df.id,
                'file_link', df.FILE_LINK,
                'description', df.DESCRIPTION,
                'version', df.VERSION
            )) as DATA_FILE,
            json_agg(DISTINCT jsonb_build_object(
                'id', bm.id,
                'biological_material_id', bm.BIOLOGICAL_MATERIAL_ID,
                'external_id', bm.EXTERNAL_ID,
                'organism', bm.ORGANISM,
                'genus', bm.GENUS,
                'species', bm.SPECIES,
                'infraspecific_name', bm.INFRASPECIFIC_NAME,
                'latitude', bm.LATITUDE,
                'longitude', bm.LONGITUDE,
                'altitude', bm.ALTITUDE,
                'coordinate_uncertainty', bm.COORDINATE_UNCERTAINTY,
                'preprocessing', bm.PREPROCESSING,
                'source_id', bm.SOURCE_ID,
                'source_doi', bm.SOURCE_DOI,
                'source_accession_number', bm.SOURCE_ACCESSION_NUMBER,
                'source_accession_name', bm.SOURCE_ACCESSION_NAME,
                'source_institution_code', bm.SOURCE_INSTITUTION_CODE,
                'source_institution_name', bm.SOURCE_INSTITUTION_NAME,
                'source_other_ids', bm.SOURCE_OTHER_IDS,
                'source_latitude', bm.SOURCE_LATITUDE,
                'source_longitude', bm.SOURCE_LONGITUDE,
                'source_altitude', bm.SOURCE_ALTITUDE,
                'source_coordinate_uncertainty', bm.SOURCE_COORDINATE_UNCERTAINTY,
                'source_description', bm.SOURCE_DESCRIPTION
            )) as BIOLOGICAL_MATERIAL,
            json_agg(DISTINCT jsonb_build_object(
                'id', e.id,
                'parameter', e.PARAMETER,
                'parameter_value', e.PARAMETER_VALUE
            )) as ENVIRONMENT,
            json_agg(DISTINCT jsonb_build_object(
                'id', ef.id,
                'factor_type', ef.FACTOR_TYPE,
                'factor_description', ef.FACTOR_DESCRIPTION,
                'factor_values', ef.FACTOR_VALUES
            )) as EXPERIMENTAL_FACTOR,
            json_agg(DISTINCT jsonb_build_object(
                'id', ev.id,
                'event_type', ev.EVENT_TYPE,
                'accession_number', ev.ACCESSION_NUMBER,
                'description', ev.DESCRIPTION,
                'event_date', ev.EVENT_DATE
            )) as EVENT,
            json_agg(DISTINCT jsonb_build_object(
                'id', ou.id,
                'observation_unit_id', ou.OBSERVATION_UNIT_ID,
                'observation_unit_type', ou.OBSERVATION_UNIT_TYPE,
                'external_id', ou.EXTERNAL_ID,
                'spatial_distribution', ou.SPATIAL_DISTRIBUTION,
                'factor_values', ou.FACTOR_VALUES
            )) as OBSERVATION_UNIT,
            json_agg(DISTINCT jsonb_build_object(
                'id', sa.id,
                'sample_id', sa.SAMPLE_ID,
                'development_stage', sa.DEVELOPMENT_STAGE,
                'anatomical_entity', sa.ANATOMICAL_ENTITY,
                'description', sa.DESCRIPTION,
                'collection_date', sa.COLLECTION_DATE,
                'external_id', sa.EXTERNAL_ID
            )) as SAMPLE,
            json_agg(DISTINCT jsonb_build_object(
                'id', ov.id,
                'variable_id', ov.VARIABLE_ID,
                'variable_name', ov.VARIABLE_NAME,
                'accession_number', ov.ACCESSION_NUMBER,
                'trait_name', ov.TRAIT_NAME,
                'trait_entity', ov.TRAIT_ENTITY,
                'trait_entity_accession_number', ov.TRAIT_ENTITY_ACCESSION_NUMBER,
                'trait_characteristic', ov.TRAIT_CHARACTERISTIC,
                'trait_characteristic_accession_number', ov.TRAIT_CHARACTERISTIC_ACCESSION_NUMBER,
                'trait_accession_number', ov.TRAIT_ACCESSION_NUMBER,
                'method_name', ov.METHOD_NAME,
                'method_accession_number', ov.METHOD_ACCESSION_NUMBER,
                'method_description', ov.METHOD_DESCRIPTION,
                'method_reference', ov.METHOD_REFERENCE,
                'scale_name', ov.SCALE_NAME,
                'scale_accession_number', ov.SCALE_ACCESSION_NUMBER,
                'time_scale', ov.TIME_SCALE
            )) as OBSERVED_VARIABLE
        FROM study_data s
        LEFT JOIN PERSON p ON s.id = p.STUDY_ID
        LEFT JOIN DATA_FILE df ON s.id = df.STUDY_ID
        LEFT JOIN BIOLOGICAL_MATERIAL bm ON s.id = bm.STUDY_ID
        LEFT JOIN ENVIRONMENT e ON s.id = e.STUDY_ID
        LEFT JOIN EXPERIMENTAL_FACTOR ef ON s.id = ef.STUDY_ID
        LEFT JOIN EVENT ev ON s.id = ev.STUDY_ID
        LEFT JOIN OBSERVATION_UNIT ou ON s.id = ou.STUDY_ID
        LEFT JOIN SAMPLE sa ON s.id = sa.STUDY_ID
        LEFT JOIN OBSERVED_VARIABLE ov ON s.id = ov.STUDY_ID
        GROUP BY 
            s.id,
            s.STUDY_ID,
            s.STUDY_TITLE,
            s.STUDY_DESCRIPTION,
            s.STUDY_START_DATE,
            s.STUDY_END_DATE,
            s.CONTACT_INSTITUTION,
            s.LOCATION_COUNTRY,
            s.SITE_NAME,
            s.LOCATION_LATITUDE,
            s.LOCATION_LONGITUDE,
            s.LOCATION_ALTITUDE,
            s.EXPERIMENTAL_DESIGN_DESCRIPTION,
            s.EXPERIMENTAL_DESIGN_TYPE,
            s.OBSERVATION_UNIT_LEVEL_HIERARCHY,
            s.OBSERVATION_UNIT_DESCRIPTION,
            s.GROWTH_FACILITY_DESCRIPTION,
            s.GROWTH_FACILITY_TYPE,
            s.CULTURAL_PRACTICES,
            s.EXPERIMENTAL_DESIGN_MAP,
            s.INVESTIGATION_TITLE
    """, (study_id, investigation_db_id))
    return cursor.fetchone()

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
    for frontend_field, value in data.items():
        if frontend_field in FRONTEND_TO_BACKEND:
            backend_field = FRONTEND_TO_BACKEND[frontend_field]
            if backend_field in BACKEND_TO_DB:
                db_field = BACKEND_TO_DB[backend_field]
                result[db_field] = value
            else:
                result[backend_field] = value
        else:
            result[frontend_field] = value
    return result 