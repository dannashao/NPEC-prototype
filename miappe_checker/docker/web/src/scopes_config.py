"""
Configuration for MIAPPE scopes and their fields.
This file defines the structure of all scopes and their fields based on the database schema.
"""

SCOPES = {
    'INVESTIGATION': {
        'requirement': 0,
        'fields': {
            'investigationId': {
                'requirement': 0,
                'definition': 'Unique identifier for the investigation',
                'example': 'INV-001'
            },
            'investigationTitle': {
                'requirement': 0,
                'definition': 'Title of the investigation',
                'example': 'Study of plant growth under different conditions'
            },
            'investigationDescription': {
                'requirement': 1,
                'definition': 'Detailed description of the investigation',
                'example': 'This investigation aims to study...'
            },
            'submissionDate': {
                'requirement': 1,
                'definition': 'Date when the investigation was submitted',
                'example': '2024-03-29'
            },
            'publicReleaseDate': {
                'requirement': 1,
                'definition': 'Date when the investigation becomes publicly available',
                'example': '2024-04-29'
            },
            'license': {
                'requirement': 1,
                'definition': 'License under which the data is released',
                'example': 'CC BY 4.0'
            },
            'miappeVersion': {
                'requirement': 1,
                'definition': 'Version of MIAPPE standard used',
                'example': '1.0'
            },
            'associatedPublication': {
                'requirement': 1,
                'definition': 'Publications associated with this investigation',
                'example': 'DOI: 10.1234/example'
            }
        }
    },
    'STUDY': {
        'requirement': 0,
        'fields': {
            'studyId': {
                'requirement': 0,
                'definition': 'Unique identifier for the study',
                'example': 'STU-001'
            },
            'studyTitle': {
                'requirement': 0,
                'definition': 'Title of the study',
                'example': 'Growth experiment with different light conditions'
            },
            'studyDescription': {
                'requirement': 0,
                'definition': 'Detailed description of the study',
                'example': 'This study investigates...'
            },
            'studyStartDate': {
                'requirement': 1,
                'definition': 'Start date of the study',
                'example': '2024-03-29'
            },
            'studyEndDate': {
                'requirement': 1,
                'definition': 'End date of the study',
                'example': '2024-04-29'
            },
            'contactInstitution': {
                'requirement': 0,
                'definition': 'Institution responsible for the study',
                'example': 'University of Example'
            },
            'locationCountry': {
                'requirement': 1,
                'definition': 'Country where the study was conducted (ISO 3166-1 alpha-2)',
                'example': 'US'
            },
            'siteName': {
                'requirement': 1,
                'definition': 'Name of the site where the study was conducted',
                'example': 'Research Farm A'
            },
            'locationLatitude': {
                'requirement': 1,
                'definition': 'Latitude of the study location',
                'example': '40.7128'
            },
            'locationLongitude': {
                'requirement': 1,
                'definition': 'Longitude of the study location',
                'example': '-74.0060'
            },
            'locationAltitude': {
                'requirement': 1,
                'definition': 'Altitude of the study location in meters',
                'example': '100'
            },
            'experimentalDesignDescription': {
                'requirement': 1,
                'definition': 'Description of the experimental design',
                'example': 'Randomized complete block design'
            },
            'experimentalDesignType': {
                'requirement': 1,
                'definition': 'Type of experimental design',
                'example': 'RCBD'
            },
            'observationUnitLevelHierarchy': {
                'requirement': 1,
                'definition': 'Hierarchy of observation units',
                'example': 'block > plot > plant'
            },
            'observationUnitDescription': {
                'requirement': 1,
                'definition': 'Description of observation units',
                'example': 'Each plot contains 10 plants'
            },
            'growthFacilityDescription': {
                'requirement': 1,
                'definition': 'Description of the growth facility',
                'example': 'Greenhouse with controlled environment'
            },
            'growthFacilityType': {
                'requirement': 1,
                'definition': 'Type of growth facility',
                'example': 'greenhouse'
            },
            'culturalPractices': {
                'requirement': 1,
                'definition': 'Cultural practices applied during the study',
                'example': 'Regular watering, fertilization'
            }
        }
    },
    'PERSON': {
        'requirement': 1,
        'fields': {
            'name': {
                'requirement': 0,
                'definition': 'Full name of the person',
                'example': 'John Doe'
            },
            'role': {
                'requirement': 0,
                'definition': 'Role(s) of the person in the study',
                'example': 'Principal Investigator, Data Curator'
            },
            'affiliation': {
                'requirement': 0,
                'definition': 'Institution(s) the person is affiliated with',
                'example': 'University of Example, Department of Biology'
            }
        }
    },
    'DATA_FILE': {
        'requirement': 1,
        'fields': {
            'fileLink': {
                'requirement': 0,
                'definition': 'Link to the data file',
                'example': 'https://example.com/data.csv'
            },
            'description': {
                'requirement': 0,
                'definition': 'Description of the data file',
                'example': 'Raw measurements of plant height'
            },
            'version': {
                'requirement': 1,
                'definition': 'Version of the data file',
                'example': '1.0'
            }
        }
    },
    'BIOLOGICAL_MATERIAL': {
        'requirement': 1,
        'fields': {
            'biologicalMaterialId': {
                'requirement': 0,
                'definition': 'Unique identifier for the biological material',
                'example': 'BM-001'
            },
            'externalId': {
                'requirement': 1,
                'definition': 'External identifiers for the biological material',
                'example': 'GRIN:12345'
            },
            'organism': {
                'requirement': 0,
                'definition': 'Organism name',
                'example': 'Arabidopsis thaliana'
            },
            'genus': {
                'requirement': 1,
                'definition': 'Genus name',
                'example': 'Arabidopsis'
            },
            'species': {
                'requirement': 1,
                'definition': 'Species name',
                'example': 'thaliana'
            },
            'infraspecificName': {
                'requirement': 1,
                'definition': 'Infraspecific name (variety, cultivar, etc.)',
                'example': 'Col-0'
            },
            'latitude': {
                'requirement': 1,
                'definition': 'Latitude of the biological material origin',
                'example': '40.7128'
            },
            'longitude': {
                'requirement': 1,
                'definition': 'Longitude of the biological material origin',
                'example': '-74.0060'
            },
            'altitude': {
                'requirement': 1,
                'definition': 'Altitude of the biological material origin',
                'example': '100'
            },
            'coordinateUncertainty': {
                'requirement': 1,
                'definition': 'Uncertainty of the coordinates in meters',
                'example': '10'
            },
            'preprocessing': {
                'requirement': 1,
                'definition': 'Preprocessing steps applied to the biological material',
                'example': 'Surface sterilization, Stratification'
            },
            'sourceId': {
                'requirement': 1,
                'definition': 'Identifier of the material source',
                'example': 'SRC-001'
            },
            'sourceDoi': {
                'requirement': 1,
                'definition': 'DOI of the material source',
                'example': '10.1234/example'
            },
            'sourceAccessionNumber': {
                'requirement': 1,
                'definition': 'Accession number of the material source',
                'example': 'ACC-001'
            },
            'sourceAccessionName': {
                'requirement': 1,
                'definition': 'Name of the material source accession',
                'example': 'Col-0 wild type'
            },
            'sourceInstitutionCode': {
                'requirement': 1,
                'definition': 'Institution code of the material source',
                'example': 'ABRC'
            },
            'sourceInstitutionName': {
                'requirement': 1,
                'definition': 'Institution name of the material source',
                'example': 'Arabidopsis Biological Resource Center'
            },
            'sourceOtherIds': {
                'requirement': 1,
                'definition': 'Other identifiers of the material source',
                'example': '{"GRIN": "12345", "NCBI": "3702"}'
            },
            'sourceLatitude': {
                'requirement': 1,
                'definition': 'Latitude of the material source',
                'example': '40.7128'
            },
            'sourceLongitude': {
                'requirement': 1,
                'definition': 'Longitude of the material source',
                'example': '-74.0060'
            },
            'sourceAltitude': {
                'requirement': 1,
                'definition': 'Altitude of the material source',
                'example': '100'
            },
            'sourceCoordinateUncertainty': {
                'requirement': 1,
                'definition': 'Uncertainty of the source coordinates',
                'example': '10'
            },
            'sourceDescription': {
                'requirement': 1,
                'definition': 'Description of the material source',
                'example': 'Wild type accession collected in 1983'
            }
        }
    },
    'ENVIRONMENT': {
        'requirement': 1,
        'fields': {
            'parameter': {
                'requirement': 0,
                'definition': 'Environmental parameter name',
                'example': 'Temperature'
            },
            'parameterValue': {
                'requirement': 0,
                'definition': 'Value of the environmental parameter',
                'example': '22'
            }
        }
    },
    'EXPERIMENTAL_FACTOR': {
        'requirement': 1,
        'fields': {
            'factorType': {
                'requirement': 0,
                'definition': 'Type of experimental factor',
                'example': 'Light intensity'
            },
            'factorDescription': {
                'requirement': 0,
                'definition': 'Description of the experimental factor',
                'example': 'Different light intensities for plant growth'
            },
            'factorValues': {
                'requirement': 0,
                'definition': 'Values of the experimental factor',
                'example': 'High, Medium, Low'
            }
        }
    },
    'EVENT': {
        'requirement': 1,
        'fields': {
            'eventType': {
                'requirement': 0,
                'definition': 'Type of event',
                'example': 'Planting'
            },
            'accessionNumber': {
                'requirement': 1,
                'definition': 'Accession number for the event',
                'example': 'EVT-001'
            },
            'description': {
                'requirement': 0,
                'definition': 'Description of the event',
                'example': 'Seeds were planted in pots'
            },
            'eventDate': {
                'requirement': 0,
                'definition': 'Date(s) of the event',
                'example': '2024-03-29'
            }
        }
    },
    'OBSERVATION_UNIT': {
        'requirement': 1,
        'fields': {
            'observationUnitId': {
                'requirement': 0,
                'definition': 'Unique identifier for the observation unit',
                'example': 'OU-001'
            },
            'observationUnitType': {
                'requirement': 0,
                'definition': 'Type of observation unit',
                'example': 'plot'
            },
            'externalId': {
                'requirement': 1,
                'definition': 'External identifier for the observation unit',
                'example': 'EXT-001'
            },
            'spatialDistribution': {
                'requirement': 1,
                'definition': 'Spatial distribution of the observation unit',
                'example': '{"row": 1, "column": 2}'
            },
            'factorValues': {
                'requirement': 1,
                'definition': 'Values of experimental factors for this unit',
                'example': '{"Light": "High", "Temperature": "22"}'
            }
        }
    },
    'SAMPLE': {
        'requirement': 1,
        'fields': {
            'sampleId': {
                'requirement': 0,
                'definition': 'Unique identifier for the sample',
                'example': 'SMP-001'
            },
            'developmentStage': {
                'requirement': 1,
                'definition': 'Development stage of the sample',
                'example': 'Flowering'
            },
            'anatomicalEntity': {
                'requirement': 1,
                'definition': 'Anatomical entity of the sample',
                'example': 'Leaf'
            },
            'description': {
                'requirement': 0,
                'definition': 'Description of the sample',
                'example': 'Mature leaf from the third node'
            },
            'collectionDate': {
                'requirement': 0,
                'definition': 'Date when the sample was collected',
                'example': '2024-03-29'
            },
            'externalId': {
                'requirement': 1,
                'definition': 'External identifier for the sample',
                'example': 'EXT-001'
            }
        }
    },
    'OBSERVED_VARIABLE': {
        'requirement': 1,
        'fields': {
            'variableId': {
                'requirement': 0,
                'definition': 'Unique identifier for the observed variable',
                'example': 'VAR-001'
            },
            'variableName': {
                'requirement': 0,
                'definition': 'Name of the observed variable',
                'example': 'Plant height'
            },
            'accessionNumber': {
                'requirement': 1,
                'definition': 'Accession number for the variable',
                'example': 'TO:0000207'
            },
            'traitName': {
                'requirement': 0,
                'definition': 'Name of the trait',
                'example': 'Plant height'
            },
            'traitEntity': {
                'requirement': 1,
                'definition': 'Entity being measured',
                'example': 'Plant'
            },
            'traitEntityAccessionNumber': {
                'requirement': 1,
                'definition': 'Accession number for the trait entity',
                'example': 'PO:0009003'
            },
            'traitCharacteristic': {
                'requirement': 1,
                'definition': 'Characteristic being measured',
                'example': 'Height'
            },
            'traitCharacteristicAccessionNumber': {
                'requirement': 1,
                'definition': 'Accession number for the trait characteristic',
                'example': 'PATO:0000124'
            },
            'traitAccessionNumber': {
                'requirement': 1,
                'definition': 'Accession number for the trait',
                'example': 'TO:0000207'
            },
            'methodName': {
                'requirement': 0,
                'definition': 'Name of the measurement method',
                'example': 'Ruler measurement'
            },
            'methodAccessionNumber': {
                'requirement': 1,
                'definition': 'Accession number for the method',
                'example': 'CO:123'
            },
            'methodDescription': {
                'requirement': 0,
                'definition': 'Description of the measurement method',
                'example': 'Using a ruler to measure from soil to tip'
            },
            'methodReference': {
                'requirement': 1,
                'definition': 'Reference for the measurement method',
                'example': 'DOI: 10.1234/example'
            },
            'scaleName': {
                'requirement': 0,
                'definition': 'Name of the measurement scale',
                'example': 'Centimeter'
            },
            'scaleAccessionNumber': {
                'requirement': 1,
                'definition': 'Accession number for the scale',
                'example': 'UO:0000015'
            },
            'timeScale': {
                'requirement': 1,
                'definition': 'Time scale for the measurement',
                'example': 'Days after planting'
            }
        }
    }
} 