# MIAPPE PostgreSQL Schema Documentation

## Overview

This document describes the PostgreSQL database schema used for storing MIAPPE (Minimum Information About a Plant Phenotyping Experiment) metadata. The schema is designed to align with the MIAPPE standard while providing efficient data storage and retrieval capabilities, with support for MongoDB field bindings.

## Quick Links
[MIAPPE_Checklist-Data-Model-v1.1](https://github.com/MIAPPE/MIAPPE/tree/v1.1.2/MIAPPE_Checklist-Data-Model-v1.1)
[Current schema](miappe_checker/deployments/miappe=postgres-init.yml)


## Core Concepts

### Investigation (Top-Level)
The `investigation` table serves as the top-level concept in our schema, representing a complete research project or experiment. This aligns with the ISA (Investigation-Study-Assay) framework that MIAPPE is based on.

Key fields:
- `id`: UUID primary key
- `investigation_id`: Unique identifier in format "institution:accession_number"
- `title`: Human-readable string summarizing the investigation
- `description`: Detailed description of the research project
- `submission_date`: When the investigation was submitted (ISO 8601 with timezone)
- `public_release_date`: When the data becomes publicly available (ISO 8601 with timezone)
- `license`: Creative Commons license (CC BY, CC BY-SA, CC BY-NC, CC BY-NC-SA, or "Unreported")
- `miappe_version`: Version of MIAPPE standard used
- `associated_publication`: Array of publication references (DOIs recommended)

All fields have corresponding `*_binding` fields for MongoDB integration.

### Study
The `study` table represents individual experiments within an investigation. Each study must belong to exactly one investigation, following MIAPPE's hierarchical structure.

Key fields:
- `id`: UUID primary key
- `investigation_id`: Reference to parent investigation
- `study_id`: Unique identifier in format "institution:accession_number" or URL
- `study_title`: Human-readable title
- `study_description`: Detailed description
- `study_start_date`: Start date/time (ISO 8601 with timezone)
- `study_end_date`: End date/time (ISO 8601 with timezone)
- `contact_institution`: Institution responsible for the study
- `location_country`: ISO 3166 2-letter country code
- `site_name`: Name of experimental site
- `location_*`: Geographic coordinates (latitude, longitude, altitude)
- `experimental_design_*`: Design and methodology details
- `growth_facility_*`: Information about the growth environment
- `cultural_practices`: Description of cultural practices
- `experimental_design_map`: Array of design map references

All fields have corresponding `*_binding` fields for MongoDB integration.

## Supporting Entities

### Person and Study-Person
The `person` and `study_person` tables implement MIAPPE's requirement for tracking researchers and their roles in studies.

Key fields:
- `name`: Full name or publication name
- `email`: Electronic mail address
- `person_id`: ORCID identifier (recommended)
- `role`: Array of roles (e.g., "data submitter", "author", "corresponding author")
- `affiliation`: Array of institutional affiliations

All fields have corresponding `*_binding` fields for MongoDB integration.

### Biological Material
The `biological_material` table stores detailed information about the biological materials used in studies.

Key fields:
- `biological_material_id`: Unique identifier within investigation
- `external_id`: Array of external identifiers (e.g., EBI Biosamples ID)
- `organism`: NCBI taxon ID
- `genus`, `species`: Taxonomic information
- `infraspecific_name`: JSONB for taxonomic ranks (subspecies, cultivar, etc.)
- `source_*`: Detailed source information
- `preprocessing`: Array of preprocessing steps

All fields have corresponding `*_binding` fields for MongoDB integration.

### Environment and Experimental Factors
These tables capture environmental conditions and experimental treatments.

Key fields:
- `environment`:
  - `parameter`: From MIAPPE Appendix I
  - `parameter_value`: Corresponding value
- `experimental_factor`:
  - `factor_type`: From MIAPPE Appendix II
  - `factor_description`: Detailed description
  - `factor_values`: Array of at least 2 possible values

All fields have corresponding `*_binding` fields for MongoDB integration.

### Observation Units and Samples
These tables represent the physical entities being studied.

Key fields:
- `observation_unit`:
  - `observation_unit_id`: Locally unique identifier
  - `observation_unit_type`: Restricted to standard types (study, block, sub-block, plot, sub-plot, pot, plant)
  - `spatial_distribution`: JSONB for spatial coordinates
  - `factor_values`: Array of applied factors
- `sample`:
  - `development_stage`: Plant Ontology or BBCH scale term
  - `anatomical_entity`: Plant Ontology term
  - `collection_date`: ISO 8601 with timezone

All fields have corresponding `*_binding` fields for MongoDB integration.

### Observed Variables
The `observed_variable` table captures what was measured and how.

Key fields:
- `variable_id`: Crop Ontology naming convention
- `trait_name`: Name of the trait
- `trait_entity`: Plant Ontology term
- `trait_characteristic`: PATO term
- `method_name`: Crop Ontology term
- `scale_name`: Unique scale identifier

All fields have corresponding `*_binding` fields for MongoDB integration.

## Technical Implementation Details

### Data Types and Constraints
- UUID primary keys for all tables
- JSONB for flexible data structures (e.g., factor values, spatial distribution)
- DECIMAL for precise numeric values (coordinates, measurements)
- TEXT[] for arrays of strings (e.g., roles, affiliations)
- TIMESTAMP WITH TIME ZONE for all dates
- Appropriate foreign key constraints with CASCADE deletion
- Unique constraints where needed
- CHECK constraints for enumerated values
- TEXT fields for MongoDB bindings

### Performance Optimization
- Indexes on foreign keys
- Indexes on frequently queried fields
- JSONB for flexible but queryable data structures
- Array types for multiple values
- Efficient indexing strategy for hierarchical queries

### Data Integrity
- Automatic timestamp management (created_at, updated_at)
- Triggers for maintaining updated_at
- Appropriate constraints for data validation
- NOT NULL constraints for required fields
- Format validation for identifiers and codes

## MongoDB Integration

### Binding Fields
Each MIAPPE field has a corresponding binding field that stores the MongoDB field path. This allows:
- Direct mapping between MIAPPE fields and MongoDB data
- Real-time synchronization of values
- Flexible data source integration
- Support for multiple data formats

### Binding Field Format
- Naming convention: `field_name_binding`
- Type: TEXT
- Contains: MongoDB field path (e.g., "plant.sensor.temperature")
- Nullable: Yes

## Usage Considerations

1. **Data Entry**
   - Start with investigation creation
   - Add studies to the investigation
   - Populate supporting entities as needed
   - Use appropriate ontology terms
   - Follow naming conventions
   - Set up MongoDB bindings where applicable

2. **Querying**
   - Use indexes for efficient retrieval
   - Leverage JSONB for flexible queries
   - Consider materialized views for common queries
   - Use array operations for multiple values
   - Join with MongoDB data using bindings

3. **Maintenance**
   - Regular index maintenance
   - Monitor JSONB field sizes
   - Backup and recovery procedures
   - Ontology term updates
   - MongoDB binding validation

## Future Considerations

1. **Potential Extensions**
   - Additional indexes for specific query patterns
   - Materialized views for common reports
   - Partitioning for large tables
   - Additional ontology integrations
   - Enhanced MongoDB binding features

2. **Performance Optimization**
   - Query optimization
   - Index tuning
   - Connection pooling
   - Caching strategies
   - Binding field indexing

3. **Integration**
   - API endpoints
   - Data validation
   - Export capabilities
   - Ontology validation
   - MongoDB sync optimization 