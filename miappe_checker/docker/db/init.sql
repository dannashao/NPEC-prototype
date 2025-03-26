-- Create the database
CREATE DATABASE miappe;

-- Connect to the database
\c miappe

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create investigation table (top-level concept)
CREATE TABLE investigation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    investigation_id TEXT NOT NULL, -- Format: institution:accession_number
    title TEXT NOT NULL,
    description TEXT,
    submission_date TIMESTAMP WITH TIME ZONE,
    public_release_date TIMESTAMP WITH TIME ZONE,
    license TEXT CHECK (license LIKE 'CC BY%' OR license LIKE 'CC BY-SA%' OR license LIKE 'CC BY-NC%' OR license LIKE 'CC BY-NC-SA%' OR license = 'Unreported'),
    miappe_version TEXT NOT NULL,
    associated_publication TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(investigation_id),
    UNIQUE(title)
);

-- Create study table (belongs to investigation)
CREATE TABLE study (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    investigation_id UUID NOT NULL REFERENCES investigation(id) ON DELETE CASCADE,
    study_id TEXT NOT NULL, -- Format: institution:accession_number or URL
    study_title TEXT NOT NULL,
    study_description TEXT,
    study_start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    study_end_date TIMESTAMP WITH TIME ZONE,
    contact_institution TEXT NOT NULL,
    location_country TEXT NOT NULL CHECK (char_length(location_country) = 2), -- ISO 3166 2-letter code
    site_name TEXT NOT NULL,
    location_latitude DECIMAL,
    location_longitude DECIMAL,
    location_altitude DECIMAL,
    experimental_design_description TEXT NOT NULL,
    experimental_design_type TEXT, -- Crop Ontology term
    observation_unit_level_hierarchy TEXT, -- Format: level>level
    observation_unit_description TEXT NOT NULL,
    growth_facility_description TEXT NOT NULL,
    growth_facility_type TEXT, -- Crop Ontology term
    cultural_practices TEXT,
    experimental_design_map TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(investigation_id, study_id)
);

-- Create person table (can be associated with multiple studies)
CREATE TABLE person (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT,
    person_id TEXT, -- ORCID identifier
    role TEXT[] NOT NULL, -- Array of roles
    affiliation TEXT[] NOT NULL, -- Array of affiliations
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create study_person junction table
CREATE TABLE study_person (
    study_id UUID REFERENCES study(id) ON DELETE CASCADE,
    person_id UUID REFERENCES person(id) ON DELETE CASCADE,
    PRIMARY KEY (study_id, person_id)
);

-- Create data_file table (belongs to study)
CREATE TABLE data_file (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    study_id UUID NOT NULL REFERENCES study(id) ON DELETE CASCADE,
    file_link TEXT NOT NULL, -- URL or file name
    description TEXT NOT NULL, -- Standard format name or organization description
    version TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create biological_material table (belongs to study)
CREATE TABLE biological_material (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    study_id UUID NOT NULL REFERENCES study(id) ON DELETE CASCADE,
    biological_material_id TEXT NOT NULL, -- Unique within investigation
    external_id TEXT[], -- Array of external identifiers
    organism TEXT NOT NULL, -- NCBI taxon ID
    genus TEXT,
    species TEXT,
    infraspecific_name JSONB, -- Key-value pairs for taxonomic ranks
    latitude DECIMAL,
    longitude DECIMAL,
    altitude DECIMAL,
    coordinate_uncertainty DECIMAL,
    preprocessing TEXT[],
    source_id TEXT, -- Format: repository:accession
    source_doi TEXT,
    source_accession_number TEXT,
    source_accession_name TEXT,
    source_institution_code TEXT,
    source_institution_name TEXT,
    source_other_ids JSONB, -- Key-value pairs
    source_latitude DECIMAL,
    source_longitude DECIMAL,
    source_altitude DECIMAL,
    source_coordinate_uncertainty DECIMAL,
    source_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(study_id, biological_material_id)
);

-- Create environment table (belongs to study)
CREATE TABLE environment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    study_id UUID NOT NULL REFERENCES study(id) ON DELETE CASCADE,
    parameter TEXT NOT NULL, -- From Appendix I
    parameter_value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create experimental_factor table (belongs to study)
CREATE TABLE experimental_factor (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    study_id UUID NOT NULL REFERENCES study(id) ON DELETE CASCADE,
    factor_type TEXT NOT NULL, -- From Appendix II
    factor_description TEXT,
    factor_values TEXT[] NOT NULL, -- Array of at least 2 values
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create event table (belongs to study)
CREATE TABLE event (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    study_id UUID NOT NULL REFERENCES study(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL, -- Crop Ontology term
    accession_number TEXT, -- Crop Ontology term
    description TEXT,
    event_date TIMESTAMP WITH TIME ZONE[], -- Array of dates
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create observation_unit table (belongs to study)
CREATE TABLE observation_unit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    study_id UUID NOT NULL REFERENCES study(id) ON DELETE CASCADE,
    observation_unit_id TEXT NOT NULL, -- Locally unique
    observation_unit_type TEXT NOT NULL CHECK (observation_unit_type IN ('study', 'block', 'sub-block', 'plot', 'sub-plot', 'pot', 'plant')),
    external_id TEXT[],
    spatial_distribution JSONB, -- Key-value pairs
    factor_values TEXT[], -- Array of factor values
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(study_id, observation_unit_id)
);

-- Create sample table (belongs to study)
CREATE TABLE sample (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    study_id UUID NOT NULL REFERENCES study(id) ON DELETE CASCADE,
    sample_id TEXT NOT NULL,
    development_stage TEXT, -- Plant Ontology or BBCH scale term
    anatomical_entity TEXT NOT NULL, -- Plant Ontology term
    description TEXT,
    collection_date TIMESTAMP WITH TIME ZONE NOT NULL,
    external_id TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(study_id, sample_id)
);

-- Create observed_variable table (belongs to study)
CREATE TABLE observed_variable (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    study_id UUID NOT NULL REFERENCES study(id) ON DELETE CASCADE,
    variable_id TEXT NOT NULL, -- Crop Ontology naming convention
    variable_name TEXT,
    accession_number TEXT, -- Crop Ontology term
    trait_name TEXT NOT NULL,
    trait_entity TEXT, -- Plant Ontology term
    trait_entity_accession_number TEXT, -- Plant Ontology term
    trait_characteristic TEXT, -- PATO term
    trait_characteristic_accession_number TEXT, -- PATO term
    trait_accession_number TEXT, -- Crop Ontology term
    method_name TEXT NOT NULL, -- Crop Ontology term
    method_accession_number TEXT, -- Crop Ontology term
    method_description TEXT,
    method_reference TEXT,
    scale_name TEXT NOT NULL UNIQUE,
    scale_accession_number TEXT, -- Crop Ontology term
    time_scale TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(study_id, variable_id)
);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables
CREATE TRIGGER update_investigation_updated_at
    BEFORE UPDATE ON investigation
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_study_updated_at
    BEFORE UPDATE ON study
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_person_updated_at
    BEFORE UPDATE ON person
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_file_updated_at
    BEFORE UPDATE ON data_file
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_biological_material_updated_at
    BEFORE UPDATE ON biological_material
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_environment_updated_at
    BEFORE UPDATE ON environment
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_experimental_factor_updated_at
    BEFORE UPDATE ON experimental_factor
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_event_updated_at
    BEFORE UPDATE ON event
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_observation_unit_updated_at
    BEFORE UPDATE ON observation_unit
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sample_updated_at
    BEFORE UPDATE ON sample
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_observed_variable_updated_at
    BEFORE UPDATE ON observed_variable
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create indexes for better query performance
CREATE INDEX idx_study_investigation_id ON study(investigation_id);
CREATE INDEX idx_data_file_study_id ON data_file(study_id);
CREATE INDEX idx_biological_material_study_id ON biological_material(study_id);
CREATE INDEX idx_environment_study_id ON environment(study_id);
CREATE INDEX idx_experimental_factor_study_id ON experimental_factor(study_id);
CREATE INDEX idx_event_study_id ON event(study_id);
CREATE INDEX idx_observation_unit_study_id ON observation_unit(study_id);
CREATE INDEX idx_sample_study_id ON sample(study_id);
CREATE INDEX idx_observed_variable_study_id ON observed_variable(study_id);
CREATE INDEX idx_study_person_study_id ON study_person(study_id);
CREATE INDEX idx_study_person_person_id ON study_person(person_id);
