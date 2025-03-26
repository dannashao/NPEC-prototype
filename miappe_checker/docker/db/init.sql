-- Create the database
CREATE DATABASE miappe;

-- Connect to the database
\c miappe

-- Create tables for each scope
CREATE TABLE investigation (
    id SERIAL PRIMARY KEY,
    investigation_title TEXT NOT NULL,
    miappe_version TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE study (
    id SERIAL PRIMARY KEY,
    investigation_id INTEGER REFERENCES investigation(id),
    study_id TEXT NOT NULL,
    study_title TEXT NOT NULL,
    study_start_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE person (
    id SERIAL PRIMARY KEY,
    investigation_id INTEGER REFERENCES investigation(id),
    person_name TEXT NOT NULL,
    person_role TEXT NOT NULL,
    person_affiliation TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE data_file (
    id SERIAL PRIMARY KEY,
    investigation_id INTEGER REFERENCES investigation(id),
    data_file_link TEXT,
    data_file_desc TEXT,
    data_file_version TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE biological_material (
    id SERIAL PRIMARY KEY,
    investigation_id INTEGER REFERENCES investigation(id),
    biological_material_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE environment (
    id SERIAL PRIMARY KEY,
    investigation_id INTEGER REFERENCES investigation(id),
    location_country TEXT,
    site_name TEXT,
    growth_facility_desc TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE experimental_factor (
    id SERIAL PRIMARY KEY,
    investigation_id INTEGER REFERENCES investigation(id),
    sample_id TEXT,
    anatomical_entity TEXT,
    collection_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE event (
    id SERIAL PRIMARY KEY,
    investigation_id INTEGER REFERENCES investigation(id),
    event_type TEXT,
    event_date DATE,
    event_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE observation_unit (
    id SERIAL PRIMARY KEY,
    investigation_id INTEGER REFERENCES investigation(id),
    obs_unit_id TEXT NOT NULL,
    obs_unit_type TEXT NOT NULL,
    obs_unit_desc TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sample (
    id SERIAL PRIMARY KEY,
    investigation_id INTEGER REFERENCES investigation(id),
    sample_id TEXT,
    sample_type TEXT,
    sample_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE observed_variable (
    id SERIAL PRIMARY KEY,
    investigation_id INTEGER REFERENCES investigation(id),
    variable_id TEXT NOT NULL,
    trait_name TEXT NOT NULL,
    method_name TEXT NOT NULL,
    scale_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables to automatically update the updated_at column
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