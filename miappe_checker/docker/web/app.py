from flask import Flask, render_template, request, jsonify, flash, Blueprint
from pymongo import MongoClient
import logging
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.models.miappe_schema import MIAPPESchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
           static_url_path='/miappe/static',
           static_folder='static',
           template_folder='templates')
app.secret_key = 'your-secret-key'  # Change this in production

# Create a Blueprint with url_prefix and static folder
miappe_bp = Blueprint('miappe', __name__, 
                     url_prefix='/miappe',
                     static_folder='static',
                     template_folder='templates')

# MongoDB connection
try:
    client = MongoClient("mongodb://mongodb-service:27017/plant_data")
    db = client.plant_data
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")

# PostgreSQL connection
def get_db_connection():
    return psycopg2.connect(
        host="miappe-postgres",
        database="miappe",
        user="miappe_user",
        password="miappe_password",
        cursor_factory=RealDictCursor
    )

# Load MIAPPE schema
schema = MIAPPESchema()
schema_path = os.path.join('/app/src/models/MIAPPE_Checklist_Data_Model_with_Requirements.csv')
schema.load_from_csv(schema_path)

@miappe_bp.route('/')
def index():
    # Get MongoDB columns
    try:
        sample_doc = db.plant_data.find_one()
        mongo_fields = list(sample_doc.keys()) if sample_doc else []
        mongo_fields = [f for f in mongo_fields if f != '_id']
    except Exception as e:
        logger.error(f"Failed to fetch MongoDB fields: {e}")
        mongo_fields = []

    return render_template(
        'index.html',
        scopes=schema.scopes,
        mongo_fields=mongo_fields
    )

@miappe_bp.route('/api/check_investigation', methods=['POST'])
def check_investigation():
    try:
        data = request.get_json()
        investigation_id = data.get('investigation_id')
        study_id = data.get('study_id')
        
        if not investigation_id or not study_id:
            return jsonify({
                'success': False,
                'message': 'Missing investigation_id or study_id'
            })
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # First check if investigation exists
                cur.execute("SELECT id FROM INVESTIGATION WHERE INVESTIGATION_ID = %s", (investigation_id,))
                investigation_result = cur.fetchone()
                
                if not investigation_result:
                    # Create new investigation
                    cur.execute("""
                        INSERT INTO INVESTIGATION (INVESTIGATION_ID, TITLE, DESCRIPTION, MIAPPE_VERSION)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """, (investigation_id, f"Investigation {investigation_id}", "", "1.0"))
                    investigation_result = cur.fetchone()
                
                investigation_db_id = investigation_result['id']
                
                # Check if study exists
                cur.execute("""
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
                
                result = cur.fetchone()
                
                if not result:
                    # Create new study
                    cur.execute("""
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
                    study_result = cur.fetchone()
                    
                    # Create empty result structure for new study
                    result = {
                        'id': study_result['id'],
                        'study_id': study_id,
                        'study_title': f"Study {study_id}",
                        'study_description': "",
                        'study_start_date': datetime.now(timezone.utc),
                        'study_end_date': None,
                        'contact_institution': "Not specified",
                        'location_country': "XX",
                        'site_name': "Not specified",
                        'location_latitude': None,
                        'location_longitude': None,
                        'location_altitude': None,
                        'experimental_design_description': "",
                        'experimental_design_type': "",
                        'observation_unit_level_hierarchy': "",
                        'observation_unit_description': "",
                        'growth_facility_description': "",
                        'growth_facility_type': "",
                        'cultural_practices': "",
                        'experimental_design_map': [],
                        'investigation_title': f"Investigation {investigation_id}",
                        'person': [],
                        'data_file': [],
                        'biological_material': [],
                        'environment': [],
                        'experimental_factor': [],
                        'event': [],
                        'observation_unit': [],
                        'sample': [],
                        'observed_variable': []
                    }
                
                # Convert result to dict with proper keys
                response = {
                    'success': True,
                    'exists': True,
                    'investigation': {
                        'id': str(result['id']),
                        'investigation_id': investigation_id,
                        'title': result['investigation_title']
                    },
                    'studies': [{
                        'id': str(result['id']),
                        'study_id': result['study_id'],
                        'study_title': result['study_title'],
                        'study_description': result['study_description'],
                        'study_start_date': result['study_start_date'].isoformat() if result['study_start_date'] else None,
                        'study_end_date': result['study_end_date'].isoformat() if result['study_end_date'] else None,
                        'contact_institution': result['contact_institution'],
                        'location_country': result['location_country'],
                        'site_name': result['site_name'],
                        'location_latitude': float(result['location_latitude']) if result['location_latitude'] else None,
                        'location_longitude': float(result['location_longitude']) if result['location_longitude'] else None,
                        'location_altitude': float(result['location_altitude']) if result['location_altitude'] else None,
                        'experimental_design_description': result['experimental_design_description'],
                        'experimental_design_type': result['experimental_design_type'],
                        'observation_unit_level_hierarchy': result['observation_unit_level_hierarchy'],
                        'observation_unit_description': result['observation_unit_description'],
                        'growth_facility_description': result['growth_facility_description'],
                        'growth_facility_type': result['growth_facility_type'],
                        'cultural_practices': result['cultural_practices'],
                        'experimental_design_map': result['experimental_design_map']
                    }],
                    'PERSON': result['person'] or [],
                    'DATA_FILE': result['data_file'] or [],
                    'BIOLOGICAL_MATERIAL': result['biological_material'] or [],
                    'ENVIRONMENT': result['environment'] or [],
                    'EXPERIMENTAL_FACTOR': result['experimental_factor'] or [],
                    'EVENT': result['event'] or [],
                    'OBSERVATION_UNIT': result['observation_unit'] or [],
                    'SAMPLE': result['sample'] or [],
                    'OBSERVED_VARIABLE': result['observed_variable'] or []
                }
                
                conn.commit()
                return jsonify(response)
                
    except Exception as e:
        print(f"Error in check_investigation: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error checking investigation: {str(e)}'
        })

@miappe_bp.route('/save_checklist', methods=['POST'])
def save_checklist():
    try:
        data = request.get_json()
        investigation_id = data.get('investigation_id')
        study_id = data.get('study_id')
        
        if not investigation_id or not study_id:
            return jsonify({
                'success': False,
                'message': 'Missing investigation_id or study_id'
            })
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Get study ID
                cur.execute("SELECT id FROM STUDY WHERE STUDY_ID = %s", (study_id,))
                result = cur.fetchone()
                if not result:
                    return jsonify({
                        'success': False,
                        'message': 'Study not found'
                    })
                study_id = result['id']
                
                # Update study data
                study_data = data.get('STUDY', {})
                cur.execute("""
                    UPDATE STUDY SET
                        STUDY_TITLE = %s,
                        STUDY_DESCRIPTION = %s,
                        STUDY_START_DATE = %s,
                        STUDY_END_DATE = %s,
                        CONTACT_INSTITUTION = %s,
                        LOCATION_COUNTRY = %s,
                        SITE_NAME = %s,
                        LOCATION_LATITUDE = %s,
                        LOCATION_LONGITUDE = %s,
                        LOCATION_ALTITUDE = %s,
                        EXPERIMENTAL_DESIGN_DESCRIPTION = %s,
                        EXPERIMENTAL_DESIGN_TYPE = %s,
                        OBSERVATION_UNIT_LEVEL_HIERARCHY = %s,
                        OBSERVATION_UNIT_DESCRIPTION = %s,
                        GROWTH_FACILITY_DESCRIPTION = %s,
                        GROWTH_FACILITY_TYPE = %s,
                        CULTURAL_PRACTICES = %s,
                        EXPERIMENTAL_DESIGN_MAP = %s
                    WHERE id = %s
                """, (
                    study_data.get('STUDY_TITLE'),
                    study_data.get('STUDY_DESCRIPTION'),
                    study_data.get('STUDY_START_DATE'),
                    study_data.get('STUDY_END_DATE'),
                    study_data.get('CONTACT_INSTITUTION'),
                    study_data.get('LOCATION_COUNTRY'),
                    study_data.get('SITE_NAME'),
                    study_data.get('LOCATION_LATITUDE'),
                    study_data.get('LOCATION_LONGITUDE'),
                    study_data.get('LOCATION_ALTITUDE'),
                    study_data.get('EXPERIMENTAL_DESIGN_DESCRIPTION'),
                    study_data.get('EXPERIMENTAL_DESIGN_TYPE'),
                    study_data.get('OBSERVATION_UNIT_LEVEL_HIERARCHY'),
                    study_data.get('OBSERVATION_UNIT_DESCRIPTION'),
                    study_data.get('GROWTH_FACILITY_DESCRIPTION'),
                    study_data.get('GROWTH_FACILITY_TYPE'),
                    study_data.get('CULTURAL_PRACTICES'),
                    study_data.get('EXPERIMENTAL_DESIGN_MAP'),
                    study_id
                ))
                
                # Delete existing person records
                cur.execute("DELETE FROM PERSON WHERE STUDY_ID = %s", (study_id,))
                
                # Insert new person records
                if 'PERSON' in data:
                    for person in data['PERSON']:
                        cur.execute("""
                            INSERT INTO PERSON (STUDY_ID, NAME, ROLE, AFFILIATION)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            study_id,
                            person.get('NAME'),
                            person.get('ROLE', []),
                            person.get('AFFILIATION', [])
                        ))
                
                # Delete existing data file records
                cur.execute("DELETE FROM DATA_FILE WHERE STUDY_ID = %s", (study_id,))
                
                # Insert new data file records
                if 'DATA_FILE' in data:
                    for data_file in data['DATA_FILE']:
                        cur.execute("""
                            INSERT INTO DATA_FILE (STUDY_ID, FILE_LINK, DESCRIPTION, VERSION)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            study_id,
                            data_file.get('FILE_LINK'),
                            data_file.get('DESCRIPTION'),
                            data_file.get('VERSION')
                        ))
                
                # Delete existing biological material records
                cur.execute("DELETE FROM BIOLOGICAL_MATERIAL WHERE STUDY_ID = %s", (study_id,))
                
                # Insert new biological material records
                if 'BIOLOGICAL_MATERIAL' in data:
                    for bio_material in data['BIOLOGICAL_MATERIAL']:
                        cur.execute("""
                            INSERT INTO BIOLOGICAL_MATERIAL (
                                STUDY_ID, BIOLOGICAL_MATERIAL_ID, EXTERNAL_ID, ORGANISM,
                                GENUS, SPECIES, INFRASPECIFIC_NAME, LATITUDE, LONGITUDE,
                                ALTITUDE, COORDINATE_UNCERTAINTY, PREPROCESSING,
                                SOURCE_ID, SOURCE_DOI, SOURCE_ACCESSION_NUMBER,
                                SOURCE_ACCESSION_NAME, SOURCE_INSTITUTION_CODE,
                                SOURCE_INSTITUTION_NAME, SOURCE_OTHER_IDS,
                                SOURCE_LATITUDE, SOURCE_LONGITUDE, SOURCE_ALTITUDE,
                                SOURCE_COORDINATE_UNCERTAINTY, SOURCE_DESCRIPTION
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            study_id,
                            bio_material.get('BIOLOGICAL_MATERIAL_ID'),
                            bio_material.get('EXTERNAL_ID'),
                            bio_material.get('ORGANISM'),
                            bio_material.get('GENUS'),
                            bio_material.get('SPECIES'),
                            bio_material.get('INFRASPECIFIC_NAME'),
                            bio_material.get('LATITUDE'),
                            bio_material.get('LONGITUDE'),
                            bio_material.get('ALTITUDE'),
                            bio_material.get('COORDINATE_UNCERTAINTY'),
                            bio_material.get('PREPROCESSING'),
                            bio_material.get('SOURCE_ID'),
                            bio_material.get('SOURCE_DOI'),
                            bio_material.get('SOURCE_ACCESSION_NUMBER'),
                            bio_material.get('SOURCE_ACCESSION_NAME'),
                            bio_material.get('SOURCE_INSTITUTION_CODE'),
                            bio_material.get('SOURCE_INSTITUTION_NAME'),
                            bio_material.get('SOURCE_OTHER_IDS'),
                            bio_material.get('SOURCE_LATITUDE'),
                            bio_material.get('SOURCE_LONGITUDE'),
                            bio_material.get('SOURCE_ALTITUDE'),
                            bio_material.get('SOURCE_COORDINATE_UNCERTAINTY'),
                            bio_material.get('SOURCE_DESCRIPTION')
                        ))
                
                # Delete existing environment records
                cur.execute("DELETE FROM ENVIRONMENT WHERE STUDY_ID = %s", (study_id,))
                
                # Insert new environment records
                if 'ENVIRONMENT' in data:
                    for env in data['ENVIRONMENT']:
                        cur.execute("""
                            INSERT INTO ENVIRONMENT (STUDY_ID, PARAMETER, PARAMETER_VALUE)
                            VALUES (%s, %s, %s)
                        """, (
                            study_id,
                            env.get('PARAMETER'),
                            env.get('PARAMETER_VALUE')
                        ))
                
                # Delete existing experimental factor records
                cur.execute("DELETE FROM EXPERIMENTAL_FACTOR WHERE STUDY_ID = %s", (study_id,))
                
                # Insert new experimental factor records
                if 'EXPERIMENTAL_FACTOR' in data:
                    for factor in data['EXPERIMENTAL_FACTOR']:
                        cur.execute("""
                            INSERT INTO EXPERIMENTAL_FACTOR (STUDY_ID, FACTOR_TYPE, FACTOR_DESCRIPTION, FACTOR_VALUES)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            study_id,
                            factor.get('FACTOR_TYPE'),
                            factor.get('FACTOR_DESCRIPTION'),
                            factor.get('FACTOR_VALUES', [])
                        ))
                
                # Delete existing event records
                cur.execute("DELETE FROM EVENT WHERE STUDY_ID = %s", (study_id,))
                
                # Insert new event records
                if 'EVENT' in data:
                    for event in data['EVENT']:
                        cur.execute("""
                            INSERT INTO EVENT (STUDY_ID, EVENT_TYPE, ACCESSION_NUMBER, DESCRIPTION, EVENT_DATE)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            study_id,
                            event.get('EVENT_TYPE'),
                            event.get('ACCESSION_NUMBER'),
                            event.get('DESCRIPTION'),
                            event.get('EVENT_DATE', [])
                        ))
                
                # Delete existing observation unit records
                cur.execute("DELETE FROM OBSERVATION_UNIT WHERE STUDY_ID = %s", (study_id,))
                
                # Insert new observation unit records
                if 'OBSERVATION_UNIT' in data:
                    for unit in data['OBSERVATION_UNIT']:
                        cur.execute("""
                            INSERT INTO OBSERVATION_UNIT (
                                STUDY_ID, OBSERVATION_UNIT_ID, OBSERVATION_UNIT_TYPE,
                                EXTERNAL_ID, SPATIAL_DISTRIBUTION, FACTOR_VALUES
                            )
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            study_id,
                            unit.get('OBSERVATION_UNIT_ID'),
                            unit.get('OBSERVATION_UNIT_TYPE'),
                            unit.get('EXTERNAL_ID'),
                            unit.get('SPATIAL_DISTRIBUTION'),
                            unit.get('FACTOR_VALUES', [])
                        ))
                
                # Delete existing sample records
                cur.execute("DELETE FROM SAMPLE WHERE STUDY_ID = %s", (study_id,))
                
                # Insert new sample records
                if 'SAMPLE' in data:
                    for sample in data['SAMPLE']:
                        cur.execute("""
                            INSERT INTO SAMPLE (
                                STUDY_ID, SAMPLE_ID, DEVELOPMENT_STAGE,
                                ANATOMICAL_ENTITY, DESCRIPTION, COLLECTION_DATE,
                                EXTERNAL_ID
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            study_id,
                            sample.get('SAMPLE_ID'),
                            sample.get('DEVELOPMENT_STAGE'),
                            sample.get('ANATOMICAL_ENTITY'),
                            sample.get('DESCRIPTION'),
                            sample.get('COLLECTION_DATE'),
                            sample.get('EXTERNAL_ID', [])
                        ))
                
                # Delete existing observed variable records
                cur.execute("DELETE FROM OBSERVED_VARIABLE WHERE STUDY_ID = %s", (study_id,))
                
                # Insert new observed variable records
                if 'OBSERVED_VARIABLE' in data:
                    for variable in data['OBSERVED_VARIABLE']:
                        cur.execute("""
                            INSERT INTO OBSERVED_VARIABLE (
                                STUDY_ID, VARIABLE_ID, VARIABLE_NAME,
                                ACCESSION_NUMBER, TRAIT_NAME, TRAIT_ENTITY,
                                TRAIT_ENTITY_ACCESSION_NUMBER, TRAIT_CHARACTERISTIC,
                                TRAIT_CHARACTERISTIC_ACCESSION_NUMBER, TRAIT_ACCESSION_NUMBER,
                                METHOD_NAME, METHOD_ACCESSION_NUMBER, METHOD_DESCRIPTION,
                                METHOD_REFERENCE, SCALE_NAME, SCALE_ACCESSION_NUMBER,
                                TIME_SCALE
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            study_id,
                            variable.get('VARIABLE_ID'),
                            variable.get('VARIABLE_NAME'),
                            variable.get('ACCESSION_NUMBER'),
                            variable.get('TRAIT_NAME'),
                            variable.get('TRAIT_ENTITY'),
                            variable.get('TRAIT_ENTITY_ACCESSION_NUMBER'),
                            variable.get('TRAIT_CHARACTERISTIC'),
                            variable.get('TRAIT_CHARACTERISTIC_ACCESSION_NUMBER'),
                            variable.get('TRAIT_ACCESSION_NUMBER'),
                            variable.get('METHOD_NAME'),
                            variable.get('METHOD_ACCESSION_NUMBER'),
                            variable.get('METHOD_DESCRIPTION'),
                            variable.get('METHOD_REFERENCE'),
                            variable.get('SCALE_NAME'),
                            variable.get('SCALE_ACCESSION_NUMBER'),
                            variable.get('TIME_SCALE')
                        ))
                
                conn.commit()
                
                # Check if all required fields are filled
                incomplete_scopes = []
                required_scopes = ['INVESTIGATION', 'STUDY', 'PERSON']
                
                for scope in required_scopes:
                    if scope not in data or not data[scope]:
                        incomplete_scopes.append(scope)
                
                return jsonify({
                    'success': True,
                    'is_complete': len(incomplete_scopes) == 0,
                    'incomplete_scopes': incomplete_scopes
                })
                
    except Exception as e:
        print(f"Error in save_checklist: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error saving checklist: {str(e)}'
        })

@miappe_bp.route('/health')
def health():
    return jsonify({'status': 'healthy'})

# Register the blueprint
app.register_blueprint(miappe_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001) 