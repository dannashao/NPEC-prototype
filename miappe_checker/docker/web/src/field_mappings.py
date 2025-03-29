"""
Field mappings for MIAPPE metadata checker.
This file contains mappings between different naming conventions used in the application:
- Database: UPPER_SNAKE_CASE (PostgreSQL convention)
- Backend: snake_case (Python convention)
- Frontend: camelCase (JavaScript) and kebab-case (HTML)
"""

from datetime import datetime
import json
import re

# Database to Backend mappings (UPPER_SNAKE_CASE to snake_case)
DB_TO_BACKEND = {
    # Investigation fields
    'INVESTIGATION.INVESTIGATION_ID': 'investigation_id',
    'INVESTIGATION.TITLE': 'investigation_title',
    'INVESTIGATION.DESCRIPTION': 'investigation_description',
    'INVESTIGATION.SUBMISSION_DATE': 'submission_date',
    'INVESTIGATION.PUBLIC_RELEASE_DATE': 'public_release_date',
    'INVESTIGATION.LICENSE': 'license',
    'INVESTIGATION.MIAPPE_VERSION': 'miappe_version',
    'INVESTIGATION.ASSOCIATED_PUBLICATION': 'associated_publication',
    'INVESTIGATION.created_at': 'created_at',
    'INVESTIGATION.updated_at': 'updated_at',
    
    # Study fields
    'STUDY.STUDY_ID': 'study_id',
    'STUDY.STUDY_TITLE': 'study_title',
    'STUDY.STUDY_DESCRIPTION': 'study_description',
    'STUDY.STUDY_START_DATE': 'study_start_date',
    'STUDY.STUDY_END_DATE': 'study_end_date',
    'STUDY.CONTACT_INSTITUTION': 'contact_institution',
    'STUDY.LOCATION_COUNTRY': 'location_country',
    'STUDY.SITE_NAME': 'site_name',
    'STUDY.LOCATION_LATITUDE': 'location_latitude',
    'STUDY.LOCATION_LONGITUDE': 'location_longitude',
    'STUDY.LOCATION_ALTITUDE': 'location_altitude',
    'STUDY.EXPERIMENTAL_DESIGN_DESCRIPTION': 'experimental_design_description',
    'STUDY.EXPERIMENTAL_DESIGN_TYPE': 'experimental_design_type',
    'STUDY.OBSERVATION_UNIT_LEVEL_HIERARCHY': 'observation_unit_level_hierarchy',
    'STUDY.OBSERVATION_UNIT_DESCRIPTION': 'observation_unit_description',
    'STUDY.GROWTH_FACILITY_DESCRIPTION': 'growth_facility_description',
    'STUDY.GROWTH_FACILITY_TYPE': 'growth_facility_type',
    'STUDY.CULTURAL_PRACTICES': 'cultural_practices',
    'STUDY.EXPERIMENTAL_DESIGN_MAP': 'experimental_design_map',
    'STUDY.created_at': 'created_at',
    'STUDY.updated_at': 'updated_at',
    
    # Person fields
    'PERSON.NAME': 'person_name',
    'PERSON.EMAIL': 'person_email',
    'PERSON.PERSON_ID': 'person_id',
    'PERSON.ROLE': 'person_role',
    'PERSON.AFFILIATION': 'person_affiliation',
    'PERSON.created_at': 'created_at',
    'PERSON.updated_at': 'updated_at',
    
    # Data File fields
    'DATA_FILE.FILE_LINK': 'file_link',
    'DATA_FILE.DESCRIPTION': 'data_file_description',
    'DATA_FILE.VERSION': 'data_file_version',
    'DATA_FILE.created_at': 'created_at',
    'DATA_FILE.updated_at': 'updated_at',
    
    # Biological Material fields
    'BIOLOGICAL_MATERIAL.BIOLOGICAL_MATERIAL_ID': 'biological_material_id',
    'BIOLOGICAL_MATERIAL.EXTERNAL_ID': 'biological_material_external_id',
    'BIOLOGICAL_MATERIAL.ORGANISM': 'organism',
    'BIOLOGICAL_MATERIAL.GENUS': 'genus',
    'BIOLOGICAL_MATERIAL.SPECIES': 'species',
    'BIOLOGICAL_MATERIAL.INFRASPECIFIC_NAME': 'infraspecific_name',
    'BIOLOGICAL_MATERIAL.LATITUDE': 'biological_material_latitude',
    'BIOLOGICAL_MATERIAL.LONGITUDE': 'biological_material_longitude',
    'BIOLOGICAL_MATERIAL.ALTITUDE': 'biological_material_altitude',
    'BIOLOGICAL_MATERIAL.COORDINATE_UNCERTAINTY': 'biological_material_coordinate_uncertainty',
    'BIOLOGICAL_MATERIAL.PREPROCESSING': 'preprocessing',
    'BIOLOGICAL_MATERIAL.SOURCE_ID': 'source_id',
    'BIOLOGICAL_MATERIAL.SOURCE_DOI': 'source_doi',
    'BIOLOGICAL_MATERIAL.SOURCE_ACCESSION_NUMBER': 'source_accession_number',
    'BIOLOGICAL_MATERIAL.SOURCE_ACCESSION_NAME': 'source_accession_name',
    'BIOLOGICAL_MATERIAL.SOURCE_INSTITUTION_CODE': 'source_institution_code',
    'BIOLOGICAL_MATERIAL.SOURCE_INSTITUTION_NAME': 'source_institution_name',
    'BIOLOGICAL_MATERIAL.SOURCE_OTHER_IDS': 'source_other_ids',
    'BIOLOGICAL_MATERIAL.SOURCE_LATITUDE': 'source_latitude',
    'BIOLOGICAL_MATERIAL.SOURCE_LONGITUDE': 'source_longitude',
    'BIOLOGICAL_MATERIAL.SOURCE_ALTITUDE': 'source_altitude',
    'BIOLOGICAL_MATERIAL.SOURCE_COORDINATE_UNCERTAINTY': 'source_coordinate_uncertainty',
    'BIOLOGICAL_MATERIAL.SOURCE_DESCRIPTION': 'source_description',
    'BIOLOGICAL_MATERIAL.created_at': 'created_at',
    'BIOLOGICAL_MATERIAL.updated_at': 'updated_at',
    
    # Environment fields
    'ENVIRONMENT.PARAMETER': 'environment_parameter',
    'ENVIRONMENT.PARAMETER_VALUE': 'environment_parameter_value',
    'ENVIRONMENT.created_at': 'created_at',
    'ENVIRONMENT.updated_at': 'updated_at',
    
    # Experimental Factor fields
    'EXPERIMENTAL_FACTOR.FACTOR_TYPE': 'factor_type',
    'EXPERIMENTAL_FACTOR.FACTOR_DESCRIPTION': 'factor_description',
    'EXPERIMENTAL_FACTOR.FACTOR_VALUES': 'factor_values',
    'EXPERIMENTAL_FACTOR.created_at': 'created_at',
    'EXPERIMENTAL_FACTOR.updated_at': 'updated_at',
    
    # Event fields
    'EVENT.EVENT_TYPE': 'event_type',
    'EVENT.ACCESSION_NUMBER': 'event_accession_number',
    'EVENT.DESCRIPTION': 'event_description',
    'EVENT.EVENT_DATE': 'event_date',
    'EVENT.created_at': 'created_at',
    'EVENT.updated_at': 'updated_at',
    
    # Observation Unit fields
    'OBSERVATION_UNIT.OBSERVATION_UNIT_ID': 'observation_unit_id',
    'OBSERVATION_UNIT.OBSERVATION_UNIT_TYPE': 'observation_unit_type',
    'OBSERVATION_UNIT.EXTERNAL_ID': 'observation_unit_external_id',
    'OBSERVATION_UNIT.SPATIAL_DISTRIBUTION': 'spatial_distribution',
    'OBSERVATION_UNIT.FACTOR_VALUES': 'observation_unit_factor_values',
    'OBSERVATION_UNIT.created_at': 'created_at',
    'OBSERVATION_UNIT.updated_at': 'updated_at',
    
    # Sample fields
    'SAMPLE.SAMPLE_ID': 'sample_id',
    'SAMPLE.DEVELOPMENT_STAGE': 'development_stage',
    'SAMPLE.ANATOMICAL_ENTITY': 'anatomical_entity',
    'SAMPLE.DESCRIPTION': 'sample_description',
    'SAMPLE.COLLECTION_DATE': 'collection_date',
    'SAMPLE.EXTERNAL_ID': 'sample_external_id',
    'SAMPLE.created_at': 'created_at',
    'SAMPLE.updated_at': 'updated_at',
    
    # Observed Variable fields
    'OBSERVED_VARIABLE.VARIABLE_ID': 'variable_id',
    'OBSERVED_VARIABLE.VARIABLE_NAME': 'variable_name',
    'OBSERVED_VARIABLE.ACCESSION_NUMBER': 'variable_accession_number',
    'OBSERVED_VARIABLE.TRAIT_NAME': 'trait_name',
    'OBSERVED_VARIABLE.TRAIT_ENTITY': 'trait_entity',
    'OBSERVED_VARIABLE.TRAIT_ENTITY_ACCESSION_NUMBER': 'trait_entity_accession_number',
    'OBSERVED_VARIABLE.TRAIT_CHARACTERISTIC': 'trait_characteristic',
    'OBSERVED_VARIABLE.TRAIT_CHARACTERISTIC_ACCESSION_NUMBER': 'trait_characteristic_accession_number',
    'OBSERVED_VARIABLE.TRAIT_ACCESSION_NUMBER': 'trait_accession_number',
    'OBSERVED_VARIABLE.METHOD_NAME': 'method_name',
    'OBSERVED_VARIABLE.METHOD_ACCESSION_NUMBER': 'method_accession_number',
    'OBSERVED_VARIABLE.METHOD_DESCRIPTION': 'method_description',
    'OBSERVED_VARIABLE.METHOD_REFERENCE': 'method_reference',
    'OBSERVED_VARIABLE.SCALE_NAME': 'scale_name',
    'OBSERVED_VARIABLE.SCALE_ACCESSION_NUMBER': 'scale_accession_number',
    'OBSERVED_VARIABLE.TIME_SCALE': 'time_scale',
    'OBSERVED_VARIABLE.created_at': 'created_at',
    'OBSERVED_VARIABLE.updated_at': 'updated_at'
}

# Backend to Frontend mappings (snake_case to camelCase)
BACKEND_TO_FRONTEND = {
    # Investigation fields
    'investigation_id': 'investigationId',
    'investigation_title': 'investigationTitle',
    'investigation_description': 'investigationDescription',
    'submission_date': 'submissionDate',
    'public_release_date': 'publicReleaseDate',
    'license': 'license',
    'miappe_version': 'miappeVersion',
    'associated_publication': 'associatedPublication',
    'created_at': 'createdAt',
    'updated_at': 'updatedAt',
    
    # Study fields
    'study_id': 'studyId',
    'study_title': 'studyTitle',
    'study_description': 'studyDescription',
    'study_start_date': 'studyStartDate',
    'study_end_date': 'studyEndDate',
    'contact_institution': 'contactInstitution',
    'location_country': 'locationCountry',
    'site_name': 'siteName',
    'location_latitude': 'locationLatitude',
    'location_longitude': 'locationLongitude',
    'location_altitude': 'locationAltitude',
    'experimental_design_description': 'experimentalDesignDescription',
    'experimental_design_type': 'experimentalDesignType',
    'observation_unit_level_hierarchy': 'observationUnitLevelHierarchy',
    'observation_unit_description': 'observationUnitDescription',
    'growth_facility_description': 'growthFacilityDescription',
    'growth_facility_type': 'growthFacilityType',
    'cultural_practices': 'culturalPractices',
    'experimental_design_map': 'experimentalDesignMap',
    
    # Person fields
    'person_name': 'personName',
    'person_email': 'personEmail',
    'person_id': 'personId',
    'person_role': 'personRole',
    'person_affiliation': 'personAffiliation',
    
    # Data File fields
    'file_link': 'fileLink',
    'data_file_description': 'dataFileDescription',
    'data_file_version': 'dataFileVersion',
    
    # Biological Material fields
    'biological_material_id': 'biologicalMaterialId',
    'biological_material_external_id': 'biologicalMaterialExternalId',
    'organism': 'organism',
    'genus': 'genus',
    'species': 'species',
    'infraspecific_name': 'infraspecificName',
    'biological_material_latitude': 'biologicalMaterialLatitude',
    'biological_material_longitude': 'biologicalMaterialLongitude',
    'biological_material_altitude': 'biologicalMaterialAltitude',
    'biological_material_coordinate_uncertainty': 'biologicalMaterialCoordinateUncertainty',
    'preprocessing': 'preprocessing',
    'source_id': 'sourceId',
    'source_doi': 'sourceDoi',
    'source_accession_number': 'sourceAccessionNumber',
    'source_accession_name': 'sourceAccessionName',
    'source_institution_code': 'sourceInstitutionCode',
    'source_institution_name': 'sourceInstitutionName',
    'source_other_ids': 'sourceOtherIds',
    'source_latitude': 'sourceLatitude',
    'source_longitude': 'sourceLongitude',
    'source_altitude': 'sourceAltitude',
    'source_coordinate_uncertainty': 'sourceCoordinateUncertainty',
    'source_description': 'sourceDescription',
    
    # Environment fields
    'environment_parameter': 'environmentParameter',
    'environment_parameter_value': 'environmentParameterValue',
    
    # Experimental Factor fields
    'factor_type': 'factorType',
    'factor_description': 'factorDescription',
    'factor_values': 'factorValues',
    
    # Event fields
    'event_type': 'eventType',
    'event_accession_number': 'eventAccessionNumber',
    'event_description': 'eventDescription',
    'event_date': 'eventDate',
    
    # Observation Unit fields
    'observation_unit_id': 'observationUnitId',
    'observation_unit_type': 'observationUnitType',
    'observation_unit_external_id': 'observationUnitExternalId',
    'spatial_distribution': 'spatialDistribution',
    'observation_unit_factor_values': 'observationUnitFactorValues',
    
    # Sample fields
    'sample_id': 'sampleId',
    'development_stage': 'developmentStage',
    'anatomical_entity': 'anatomicalEntity',
    'sample_description': 'sampleDescription',
    'collection_date': 'collectionDate',
    'sample_external_id': 'sampleExternalId',
    
    # Observed Variable fields
    'variable_id': 'variableId',
    'variable_name': 'variableName',
    'variable_accession_number': 'variableAccessionNumber',
    'trait_name': 'traitName',
    'trait_entity': 'traitEntity',
    'trait_entity_accession_number': 'traitEntityAccessionNumber',
    'trait_characteristic': 'traitCharacteristic',
    'trait_characteristic_accession_number': 'traitCharacteristicAccessionNumber',
    'trait_accession_number': 'traitAccessionNumber',
    'method_name': 'methodName',
    'method_accession_number': 'methodAccessionNumber',
    'method_description': 'methodDescription',
    'method_reference': 'methodReference',
    'scale_name': 'scaleName',
    'scale_accession_number': 'scaleAccessionNumber',
    'time_scale': 'timeScale'
}

# Frontend to Backend mappings (camelCase to snake_case)
FRONTEND_TO_BACKEND = {v: k for k, v in BACKEND_TO_FRONTEND.items()}

# Frontend to HTML mappings (camelCase to kebab-case)
def camel_to_kebab(s):
    """Convert camelCase to kebab-case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '-', s).lower()

FRONTEND_TO_HTML = {k: camel_to_kebab(k) for k in BACKEND_TO_FRONTEND.values()}

# HTML to Frontend mappings (kebab-case to camelCase)
HTML_TO_FRONTEND = {v: k for k, v in FRONTEND_TO_HTML.items()}

# Field type definitions for proper conversion
FIELD_TYPES = {
    # Temporarily loosening the type constraints
    
    # Array fields
    # 'ROLE': list,
    # 'AFFILIATION': list,
    # 'EXTERNAL_ID': list,
    # 'PREPROCESSING': list,
    # 'FACTOR_VALUES': list,
    # 'EVENT_DATE': list,
    
    # JSONB fields
    # 'INFRASPECIFIC_NAME': dict,
    # 'SOURCE_OTHER_IDS': dict,
    # 'SPATIAL_DISTRIBUTION': dict,

    # Date fields
    # 'SUBMISSION_DATE': datetime,
    # 'PUBLIC_RELEASE_DATE': datetime,
    # 'STUDY_START_DATE': datetime,
    # 'STUDY_END_DATE': datetime,
    # 'COLLECTION_DATE': datetime,

    
    # Only keep datetime for system fields
    'created_at': datetime,
    'updated_at': datetime
}

def validate_location_country(value):
    """Validate location country code."""
    return isinstance(value, str) and len(value) == 2

def validate_observation_unit_type(value):
    """Validate observation unit type."""
    valid_types = {'study', 'block', 'sub-block', 'plot', 'sub-plot', 'pot', 'plant'}
    return value in valid_types

def validate_license(value):
    """Validate license format."""
    valid_patterns = ['CC BY', 'CC BY-SA', 'CC BY-NC', 'CC BY-NC-SA', 'Unreported']
    return any(value.startswith(pattern) for pattern in valid_patterns)

def convert_db_to_frontend(data):
    """Convert database field names to frontend field names with proper type handling."""
    if not data:
        return None
        
    result = {}
    for db_field, value in data.items():
        if db_field in DB_TO_BACKEND:
            backend_field = DB_TO_BACKEND[db_field]
            if backend_field in BACKEND_TO_FRONTEND:
                frontend_field = BACKEND_TO_FRONTEND[backend_field]
                
                # Handle field type conversion
                field_type = FIELD_TYPES.get(db_field.split('.')[-1])
                if field_type:
                    if field_type == list and isinstance(value, (list, tuple)):
                        result[frontend_field] = [str(v) for v in value]
                    elif field_type == dict and isinstance(value, (dict, str)):
                        try:
                            result[frontend_field] = json.loads(value) if isinstance(value, str) else value
                        except json.JSONDecodeError:
                            result[frontend_field] = value
                    elif field_type == datetime and value:
                        result[frontend_field] = value.isoformat() if isinstance(value, datetime) else value
                    else:
                        result[frontend_field] = value
                else:
                    result[frontend_field] = value
            else:
                result[backend_field] = value
        else:
            result[db_field] = value
    return result

def convert_frontend_to_db(data):
    """Convert frontend field names to database field names with proper type handling."""
    if not data:
        return None
        
    result = {}
    for frontend_field, value in data.items():
        if frontend_field in FRONTEND_TO_BACKEND:
            backend_field = FRONTEND_TO_BACKEND[frontend_field]
            if backend_field in DB_TO_BACKEND:
                db_field = DB_TO_BACKEND[backend_field]
                
                # Handle field type conversion
                field_type = FIELD_TYPES.get(db_field.split('.')[-1])
                if field_type:
                    if field_type == list and isinstance(value, str):
                        result[db_field] = [v.strip() for v in value.split(',')]
                    elif field_type == dict and isinstance(value, (dict, str)):
                        try:
                            result[db_field] = json.dumps(value) if isinstance(value, dict) else value
                        except (TypeError, json.JSONEncodeError):
                            result[db_field] = value
                    elif field_type == datetime and value:
                        try:
                            result[db_field] = datetime.fromisoformat(value)
                        except (ValueError, TypeError):
                            result[db_field] = value
                    else:
                        result[db_field] = value
                else:
                    result[db_field] = value
            else:
                result[backend_field] = value
        else:
            result[frontend_field] = value
    return result 