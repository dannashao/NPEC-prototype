/**
 * Field mappings for MIAPPE metadata checker.
 * This file contains mappings between different naming conventions used in the application:
 * - Database: UPPER_SNAKE_CASE (PostgreSQL convention)
 * - Backend: snake_case (Python convention)
 * - Frontend: camelCase (JavaScript) and kebab-case (HTML)
 */

// Database to Frontend mappings (UPPER_SNAKE_CASE to camelCase)
const DB_TO_FRONTEND = {
    // Investigation fields
    'INVESTIGATION_ID': 'investigationId',
    'TITLE': 'investigationTitle',
    'DESCRIPTION': 'investigationDescription',
    'SUBMISSION_DATE': 'submissionDate',
    'PUBLIC_RELEASE_DATE': 'publicReleaseDate',
    'LICENSE': 'license',
    'MIAPPE_VERSION': 'miappeVersion',
    'ASSOCIATED_PUBLICATION': 'associatedPublication',
    
    // Study fields
    'STUDY_ID': 'studyId',
    'STUDY_TITLE': 'studyTitle',
    'STUDY_DESCRIPTION': 'studyDescription',
    'STUDY_START_DATE': 'studyStartDate',
    'STUDY_END_DATE': 'studyEndDate',
    'CONTACT_INSTITUTION': 'contactInstitution',
    'LOCATION_COUNTRY': 'locationCountry',
    'SITE_NAME': 'siteName',
    'LOCATION_LATITUDE': 'locationLatitude',
    'LOCATION_LONGITUDE': 'locationLongitude',
    'LOCATION_ALTITUDE': 'locationAltitude',
    'EXPERIMENTAL_DESIGN_DESCRIPTION': 'experimentalDesignDescription',
    'EXPERIMENTAL_DESIGN_TYPE': 'experimentalDesignType',
    'OBSERVATION_UNIT_LEVEL_HIERARCHY': 'observationUnitLevelHierarchy',
    'OBSERVATION_UNIT_DESCRIPTION': 'observationUnitDescription',
    'GROWTH_FACILITY_DESCRIPTION': 'growthFacilityDescription',
    'GROWTH_FACILITY_TYPE': 'growthFacilityType',
    'CULTURAL_PRACTICES': 'culturalPractices',
    
    // Person fields
    'NAME': 'personName',
    'EMAIL': 'personEmail',
    'PERSON_ID': 'personId',
    'ROLE': 'personRole',
    'AFFILIATION': 'personAffiliation',
    
    // Data File fields
    'FILE_LINK': 'fileLink',
    'DESCRIPTION': 'dataFileDescription',
    'VERSION': 'dataFileVersion',
    
    // Biological Material fields
    'BIOLOGICAL_MATERIAL_ID': 'biologicalMaterialId',
    'EXTERNAL_ID': 'biologicalMaterialExternalId',
    'ORGANISM': 'organism',
    'GENUS': 'genus',
    'SPECIES': 'species',
    'INFRASPECIFIC_NAME': 'infraspecificName',
    'LATITUDE': 'biologicalMaterialLatitude',
    'LONGITUDE': 'biologicalMaterialLongitude',
    'ALTITUDE': 'biologicalMaterialAltitude',
    'COORDINATE_UNCERTAINTY': 'biologicalMaterialCoordinateUncertainty',
    'PREPROCESSING': 'preprocessing',
    'SOURCE_ID': 'sourceId',
    'SOURCE_DOI': 'sourceDoi',
    'SOURCE_ACCESSION_NUMBER': 'sourceAccessionNumber',
    'SOURCE_ACCESSION_NAME': 'sourceAccessionName',
    'SOURCE_INSTITUTION_CODE': 'sourceInstitutionCode',
    'SOURCE_INSTITUTION_NAME': 'sourceInstitutionName',
    'SOURCE_OTHER_IDS': 'sourceOtherIds',
    'SOURCE_LATITUDE': 'sourceLatitude',
    'SOURCE_LONGITUDE': 'sourceLongitude',
    'SOURCE_ALTITUDE': 'sourceAltitude',
    'SOURCE_COORDINATE_UNCERTAINTY': 'sourceCoordinateUncertainty',
    'SOURCE_DESCRIPTION': 'sourceDescription',
    
    // Environment fields
    'PARAMETER': 'environmentParameter',
    'PARAMETER_VALUE': 'environmentParameterValue',
    
    // Experimental Factor fields
    'FACTOR_TYPE': 'factorType',
    'FACTOR_DESCRIPTION': 'factorDescription',
    'FACTOR_VALUES': 'factorValues',
    
    // Event fields
    'EVENT_TYPE': 'eventType',
    'ACCESSION_NUMBER': 'eventAccessionNumber',
    'DESCRIPTION': 'eventDescription',
    'EVENT_DATE': 'eventDate',
    
    // Observation Unit fields
    'OBSERVATION_UNIT_ID': 'observationUnitId',
    'OBSERVATION_UNIT_TYPE': 'observationUnitType',
    'EXTERNAL_ID': 'observationUnitExternalId',
    'SPATIAL_DISTRIBUTION': 'spatialDistribution',
    'FACTOR_VALUES': 'observationUnitFactorValues',
    
    // Sample fields
    'SAMPLE_ID': 'sampleId',
    'DEVELOPMENT_STAGE': 'developmentStage',
    'ANATOMICAL_ENTITY': 'anatomicalEntity',
    'DESCRIPTION': 'sampleDescription',
    'COLLECTION_DATE': 'collectionDate',
    'EXTERNAL_ID': 'sampleExternalId',
    
    // Observed Variable fields
    'VARIABLE_ID': 'variableId',
    'VARIABLE_NAME': 'variableName',
    'ACCESSION_NUMBER': 'variableAccessionNumber',
    'TRAIT_NAME': 'traitName',
    'TRAIT_ENTITY': 'traitEntity',
    'TRAIT_ENTITY_ACCESSION_NUMBER': 'traitEntityAccessionNumber',
    'TRAIT_CHARACTERISTIC': 'traitCharacteristic',
    'TRAIT_CHARACTERISTIC_ACCESSION_NUMBER': 'traitCharacteristicAccessionNumber',
    'TRAIT_ACCESSION_NUMBER': 'traitAccessionNumber',
    'METHOD_NAME': 'methodName',
    'METHOD_ACCESSION_NUMBER': 'methodAccessionNumber',
    'METHOD_DESCRIPTION': 'methodDescription',
    'METHOD_REFERENCE': 'methodReference',
    'SCALE_NAME': 'scaleName',
    'SCALE_ACCESSION_NUMBER': 'scaleAccessionNumber',
    'TIME_SCALE': 'timeScale'
}; 