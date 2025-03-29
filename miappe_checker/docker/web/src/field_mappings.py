"""
Field mappings for MIAPPE metadata checker.
This file contains mappings between different naming conventions used in the application:
- Database: UPPER_SNAKE_CASE (PostgreSQL convention)
- Backend: snake_case (Python convention)
- Frontend: camelCase (JavaScript) and kebab-case (HTML)
"""

# Database to Backend mappings (UPPER_SNAKE_CASE to snake_case)
DB_TO_BACKEND = {
    # Investigation fields
    'INVESTIGATION_ID': 'investigation_id',
    'TITLE': 'title',
    'DESCRIPTION': 'description',
    'SUBMISSION_DATE': 'submission_date',
    'PUBLIC_RELEASE_DATE': 'public_release_date',
    'LICENSE': 'license',
    'MIAPPE_VERSION': 'miappe_version',
    'ASSOCIATED_PUBLICATION': 'associated_publication',
    
    # Study fields
    'STUDY_ID': 'study_id',
    'STUDY_TITLE': 'study_title',
    'STUDY_DESCRIPTION': 'study_description',
    'STUDY_START_DATE': 'study_start_date',
    'STUDY_END_DATE': 'study_end_date',
    'CONTACT_INSTITUTION': 'contact_institution',
    'LOCATION_COUNTRY': 'location_country',
    'SITE_NAME': 'site_name',
    'LOCATION_LATITUDE': 'location_latitude',
    'LOCATION_LONGITUDE': 'location_longitude',
    'LOCATION_ALTITUDE': 'location_altitude',
    'EXPERIMENTAL_DESIGN_DESCRIPTION': 'experimental_design_description',
    'EXPERIMENTAL_DESIGN_TYPE': 'experimental_design_type',
    'OBSERVATION_UNIT_LEVEL_HIERARCHY': 'observation_unit_level_hierarchy',
    'OBSERVATION_UNIT_DESCRIPTION': 'observation_unit_description',
    'GROWTH_FACILITY_DESCRIPTION': 'growth_facility_description',
    'GROWTH_FACILITY_TYPE': 'growth_facility_type',
    'CULTURAL_PRACTICES': 'cultural_practices',
    'EXPERIMENTAL_DESIGN_MAP': 'experimental_design_map',
    
    # Person fields
    'NAME': 'name',
    'EMAIL': 'email',
    'PERSON_ID': 'person_id',
    'ROLE': 'role',
    'AFFILIATION': 'affiliation',
    
    # Data File fields
    'FILE_LINK': 'file_link',
    'DESCRIPTION': 'description',
    'VERSION': 'version',
    
    # Biological Material fields
    'BIOLOGICAL_MATERIAL_ID': 'biological_material_id',
    'EXTERNAL_ID': 'external_id',
    'ORGANISM': 'organism',
    'GENUS': 'genus',
    'SPECIES': 'species',
    'INFRASPECIFIC_NAME': 'infraspecific_name',
    'LATITUDE': 'latitude',
    'LONGITUDE': 'longitude',
    'ALTITUDE': 'altitude',
    'COORDINATE_UNCERTAINTY': 'coordinate_uncertainty',
    'PREPROCESSING': 'preprocessing',
    'SOURCE_ID': 'source_id',
    'SOURCE_DOI': 'source_doi',
    'SOURCE_ACCESSION_NUMBER': 'source_accession_number',
    'SOURCE_ACCESSION_NAME': 'source_accession_name',
    'SOURCE_INSTITUTION_CODE': 'source_institution_code',
    'SOURCE_INSTITUTION_NAME': 'source_institution_name',
    'SOURCE_OTHER_IDS': 'source_other_ids',
    'SOURCE_LATITUDE': 'source_latitude',
    'SOURCE_LONGITUDE': 'source_longitude',
    'SOURCE_ALTITUDE': 'source_altitude',
    'SOURCE_COORDINATE_UNCERTAINTY': 'source_coordinate_uncertainty',
    'SOURCE_DESCRIPTION': 'source_description',
    
    # Environment fields
    'PARAMETER': 'parameter',
    'PARAMETER_VALUE': 'parameter_value',
    
    # Experimental Factor fields
    'FACTOR_TYPE': 'factor_type',
    'FACTOR_DESCRIPTION': 'factor_description',
    'FACTOR_VALUES': 'factor_values',
    
    # Event fields
    'EVENT_TYPE': 'event_type',
    'ACCESSION_NUMBER': 'accession_number',
    'EVENT_DATE': 'event_date',
    
    # Observation Unit fields
    'OBSERVATION_UNIT_ID': 'observation_unit_id',
    'OBSERVATION_UNIT_TYPE': 'observation_unit_type',
    'SPATIAL_DISTRIBUTION': 'spatial_distribution',
    
    # Sample fields
    'SAMPLE_ID': 'sample_id',
    'DEVELOPMENT_STAGE': 'development_stage',
    'ANATOMICAL_ENTITY': 'anatomical_entity',
    'COLLECTION_DATE': 'collection_date',
    
    # Observed Variable fields
    'VARIABLE_ID': 'variable_id',
    'VARIABLE_NAME': 'variable_name',
    'TRAIT_NAME': 'trait_name',
    'TRAIT_ENTITY': 'trait_entity',
    'TRAIT_ENTITY_ACCESSION_NUMBER': 'trait_entity_accession_number',
    'TRAIT_CHARACTERISTIC': 'trait_characteristic',
    'TRAIT_CHARACTERISTIC_ACCESSION_NUMBER': 'trait_characteristic_accession_number',
    'TRAIT_ACCESSION_NUMBER': 'trait_accession_number',
    'METHOD_NAME': 'method_name',
    'METHOD_ACCESSION_NUMBER': 'method_accession_number',
    'METHOD_DESCRIPTION': 'method_description',
    'METHOD_REFERENCE': 'method_reference',
    'SCALE_NAME': 'scale_name',
    'SCALE_ACCESSION_NUMBER': 'scale_accession_number',
    'TIME_SCALE': 'time_scale'
}

# Backend to Frontend mappings (snake_case to camelCase)
BACKEND_TO_FRONTEND = {
    # Investigation fields
    'investigation_id': 'investigationId',
    'title': 'title',
    'description': 'description',
    'submission_date': 'submissionDate',
    'public_release_date': 'publicReleaseDate',
    'license': 'license',
    'miappe_version': 'miappeVersion',
    'associated_publication': 'associatedPublication',
    
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
    'name': 'name',
    'email': 'email',
    'person_id': 'personId',
    'role': 'role',
    'affiliation': 'affiliation',
    
    # Data File fields
    'file_link': 'fileLink',
    'description': 'description',
    'version': 'version',
    
    # Biological Material fields
    'biological_material_id': 'biologicalMaterialId',
    'external_id': 'externalId',
    'organism': 'organism',
    'genus': 'genus',
    'species': 'species',
    'infraspecific_name': 'infraspecificName',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'altitude': 'altitude',
    'coordinate_uncertainty': 'coordinateUncertainty',
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
    'parameter': 'parameter',
    'parameter_value': 'parameterValue',
    
    # Experimental Factor fields
    'factor_type': 'factorType',
    'factor_description': 'factorDescription',
    'factor_values': 'factorValues',
    
    # Event fields
    'event_type': 'eventType',
    'accession_number': 'accessionNumber',
    'event_date': 'eventDate',
    
    # Observation Unit fields
    'observation_unit_id': 'observationUnitId',
    'observation_unit_type': 'observationUnitType',
    'spatial_distribution': 'spatialDistribution',
    
    # Sample fields
    'sample_id': 'sampleId',
    'development_stage': 'developmentStage',
    'anatomical_entity': 'anatomicalEntity',
    'collection_date': 'collectionDate',
    
    # Observed Variable fields
    'variable_id': 'variableId',
    'variable_name': 'variableName',
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
FRONTEND_TO_HTML = {
    # Investigation fields
    'investigationId': 'investigation-id',
    'title': 'title',
    'description': 'description',
    'submissionDate': 'submission-date',
    'publicReleaseDate': 'public-release-date',
    'license': 'license',
    'miappeVersion': 'miappe-version',
    'associatedPublication': 'associated-publication',
    
    # Study fields
    'studyId': 'study-id',
    'studyTitle': 'study-title',
    'studyDescription': 'study-description',
    'studyStartDate': 'study-start-date',
    'studyEndDate': 'study-end-date',
    'contactInstitution': 'contact-institution',
    'locationCountry': 'location-country',
    'siteName': 'site-name',
    'locationLatitude': 'location-latitude',
    'locationLongitude': 'location-longitude',
    'locationAltitude': 'location-altitude',
    'experimentalDesignDescription': 'experimental-design-description',
    'experimentalDesignType': 'experimental-design-type',
    'observationUnitLevelHierarchy': 'observation-unit-level-hierarchy',
    'observationUnitDescription': 'observation-unit-description',
    'growthFacilityDescription': 'growth-facility-description',
    'growthFacilityType': 'growth-facility-type',
    'culturalPractices': 'cultural-practices',
    'experimentalDesignMap': 'experimental-design-map',
    
    # Person fields
    'name': 'name',
    'email': 'email',
    'personId': 'person-id',
    'role': 'role',
    'affiliation': 'affiliation',
    
    # Data File fields
    'fileLink': 'file-link',
    'description': 'description',
    'version': 'version',
    
    # Biological Material fields
    'biologicalMaterialId': 'biological-material-id',
    'externalId': 'external-id',
    'organism': 'organism',
    'genus': 'genus',
    'species': 'species',
    'infraspecificName': 'infraspecific-name',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'altitude': 'altitude',
    'coordinateUncertainty': 'coordinate-uncertainty',
    'preprocessing': 'preprocessing',
    'sourceId': 'source-id',
    'sourceDoi': 'source-doi',
    'sourceAccessionNumber': 'source-accession-number',
    'sourceAccessionName': 'source-accession-name',
    'sourceInstitutionCode': 'source-institution-code',
    'sourceInstitutionName': 'source-institution-name',
    'sourceOtherIds': 'source-other-ids',
    'sourceLatitude': 'source-latitude',
    'sourceLongitude': 'source-longitude',
    'sourceAltitude': 'source-altitude',
    'sourceCoordinateUncertainty': 'source-coordinate-uncertainty',
    'sourceDescription': 'source-description',
    
    # Environment fields
    'parameter': 'parameter',
    'parameterValue': 'parameter-value',
    
    # Experimental Factor fields
    'factorType': 'factor-type',
    'factorDescription': 'factor-description',
    'factorValues': 'factor-values',
    
    # Event fields
    'eventType': 'event-type',
    'accessionNumber': 'accession-number',
    'eventDate': 'event-date',
    
    # Observation Unit fields
    'observationUnitId': 'observation-unit-id',
    'observationUnitType': 'observation-unit-type',
    'spatialDistribution': 'spatial-distribution',
    
    # Sample fields
    'sampleId': 'sample-id',
    'developmentStage': 'development-stage',
    'anatomicalEntity': 'anatomical-entity',
    'collectionDate': 'collection-date',
    
    # Observed Variable fields
    'variableId': 'variable-id',
    'variableName': 'variable-name',
    'traitName': 'trait-name',
    'traitEntity': 'trait-entity',
    'traitEntityAccessionNumber': 'trait-entity-accession-number',
    'traitCharacteristic': 'trait-characteristic',
    'traitCharacteristicAccessionNumber': 'trait-characteristic-accession-number',
    'traitAccessionNumber': 'trait-accession-number',
    'methodName': 'method-name',
    'methodAccessionNumber': 'method-accession-number',
    'methodDescription': 'method-description',
    'methodReference': 'method-reference',
    'scaleName': 'scale-name',
    'scaleAccessionNumber': 'scale-accession-number',
    'timeScale': 'time-scale'
}

# HTML to Frontend mappings (kebab-case to camelCase)
HTML_TO_FRONTEND = {v: k for k, v in FRONTEND_TO_HTML.items()} 