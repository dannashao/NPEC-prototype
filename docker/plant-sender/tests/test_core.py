import pytest
import pandas as pd
import numpy as np
from plant_sender.core import PlantDataProcessor
import json
import tempfile
import os

@pytest.fixture
def sample_config():
    config = {
        "plant1": {
            "gene_variety": "11430",
            "description": "Test plant"
        }
    }
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        json.dump(config, f)
        return f.name

@pytest.fixture
def sample_sensor_data():
    return pd.DataFrame({
        'Tmean.air': [20.5],
        'RHmean.air': [65.0],
        'Rad': [800.0]
    })

@pytest.fixture
def processor(sample_config):
    """Create a processor with the sample config"""
    proc = PlantDataProcessor("plant1", sample_config)
    proc.load_plant_config()  # Pre-load config for tests that need it
    return proc

@pytest.fixture
def valid_df():
    return pd.DataFrame({
        'Tmean.air': [20.5, 21.0],
        'RHmean.air': [65.0, 67.0],
        'Rad': [800, 850]
    })

@pytest.fixture
def invalid_df():
    return pd.DataFrame({
        'Tmean.air': [20.5, np.nan],
        'RHmean.air': [65.0, 67.0],
        'Other': [1, 2]
    })

def test_load_plant_config(processor):
    config = processor.load_plant_config()
    assert config["gene_variety"] == "11430"
    assert processor.gene_variety == "11430"

def test_load_plant_config_invalid_plant(sample_config):
    processor = PlantDataProcessor("invalid_plant", sample_config)
    with pytest.raises(ValueError, match="No configuration found for invalid_plant"):
        processor.load_plant_config()

def test_validate_sensor_data(processor, sample_sensor_data):
    is_valid, missing_columns = processor.validate_sensor_data(sample_sensor_data)
    assert is_valid is True
    assert len(missing_columns) == 0

def test_validate_sensor_data_missing_columns(processor):
    """Test validation with missing and incorrect column names"""
    invalid_data = pd.DataFrame({
        'Temperature': [20.5],  # Wrong column name
        'RHmean.air': [65.0],
        'light': [800.0]  # Wrong column name
    })
    
    result, missing_columns = processor.validate_sensor_data(invalid_data)
    
    assert result == False
    assert 'Tmean.air' in missing_columns
    assert 'Rad' in missing_columns
    assert len(missing_columns) == 2

def test_validate_sensor_data_empty(processor):
    """Test validation with empty DataFrame"""
    empty_data = pd.DataFrame()
    result, missing_columns = processor.validate_sensor_data(empty_data)
    
    assert result == False
    assert len(missing_columns) == 3  # All columns should be missing
    assert all(col in missing_columns for col in ['Tmean.air', 'RHmean.air', 'Rad'])

def test_validate_sensor_data_with_nan(processor):
    """Test validation with NaN values"""
    nan_data = pd.DataFrame({
        'Tmean.air': [np.nan],
        'RHmean.air': [65.0],
        'Rad': [800.0]
    })
    
    is_valid, missing_columns = processor.validate_sensor_data(nan_data)
    assert is_valid  # NaN values are now allowed
    assert len(missing_columns) == 0

def test_prepare_sensor_row(processor, sample_sensor_data):
    row = processor.prepare_sensor_row(sample_sensor_data.iloc[0])
    assert isinstance(row['timestamp'], str)
    assert row['temperature'] == 20.5
    assert row['humidity'] == 65.0
    assert row['light'] == 800.0

def test_prepare_form_data(processor):
    sensor_row = {
        'timestamp': '2024-03-25T10:00:00',
        'temperature': 20.5,
        'humidity': 65.0,
        'light': 800.0
    }
    form_data = processor.prepare_form_data(sensor_row)
    assert form_data['plant_name'] == 'plant1'
    assert form_data['gene_variety'] == '11430'
    assert isinstance(form_data['sensor_data'], str)

def test_prepare_form_data_without_config(processor):
    """Test form data preparation without loaded config"""
    # Explicitly unset the config
    processor.gene_variety = None
    processor.plant_config = None
    
    sensor_row = {
        'timestamp': '2024-03-25T10:00:00',
        'temperature': 20.5,
        'humidity': 65.0,
        'light': 800.0
    }
    with pytest.raises(ValueError, match="Plant configuration not loaded"):
        processor.prepare_form_data(sensor_row)

def test_prepare_form_data_json_serialization(processor):
    """Test JSON serialization in form data"""
    sensor_row = {
        'timestamp': '2024-03-25T10:00:00',
        'temperature': 20.5,
        'humidity': 65.0,
        'light': 800.0
    }
    
    form_data = processor.prepare_form_data(sensor_row)
    
    # Verify JSON structure
    sensor_data = json.loads(form_data['sensor_data'])
    assert isinstance(sensor_data, dict)
    assert sensor_data['timestamp'] == '2024-03-25T10:00:00'
    assert sensor_data['temperature'] == 20.5
    assert sensor_data['humidity'] == 65.0
    assert sensor_data['light'] == 800.0

def test_prepare_form_data_with_float_precision(processor):
    """Test handling of floating-point precision"""
    sensor_row = {
        'timestamp': '2024-03-25T10:00:00',
        'temperature': 20.555555,  # Many decimal places
        'humidity': 65.444444,
        'light': 800.666666
    }
    
    form_data = processor.prepare_form_data(sensor_row)
    sensor_data = json.loads(form_data['sensor_data'])
    
    # Verify precision is maintained correctly
    assert isinstance(sensor_data['temperature'], float)
    assert round(sensor_data['temperature'], 6) == 20.555555

def test_validate_sensor_data_valid(processor, valid_df):
    is_valid, missing_columns = processor.validate_sensor_data(valid_df)
    assert is_valid
    assert len(missing_columns) == 0

def test_validate_sensor_data_missing_columns(processor, invalid_df):
    is_valid, missing_columns = processor.validate_sensor_data(invalid_df)
    assert not is_valid
    assert 'Rad' in missing_columns

def test_validate_sensor_data_empty(processor):
    empty_df = pd.DataFrame()
    is_valid, missing_columns = processor.validate_sensor_data(empty_df)
    assert not is_valid
    assert missing_columns == {'Tmean.air', 'RHmean.air', 'Rad'}

def test_prepare_sensor_row_valid(processor, valid_df):
    row = valid_df.iloc[0]
    result = processor.prepare_sensor_row(row)
    
    assert 'timestamp' in result
    assert result['temperature'] == 20.5
    assert result['humidity'] == 65.0
    assert result['light'] == 800

def test_prepare_sensor_row_with_nan(processor, invalid_df):
    # Test with row containing NaN
    row = invalid_df.iloc[1]
    result = processor.prepare_sensor_row(row)
    
    assert 'timestamp' in result
    assert np.isnan(result['temperature'])  # Should handle NaN gracefully
    assert result['humidity'] == 67.0
    assert np.isnan(result['light'])  # Missing column should result in NaN

def test_prepare_sensor_row_missing_columns(processor):
    # Test with row missing required columns
    row = pd.Series({'Other': 1})
    result = processor.prepare_sensor_row(row)
    
    assert 'timestamp' in result
    assert np.isnan(result['temperature'])
    assert np.isnan(result['humidity'])
    assert np.isnan(result['light'])

def test_prepare_sensor_row_invalid_values(processor):
    # Test with invalid value types
    row = pd.Series({
        'Tmean.air': 'invalid',
        'RHmean.air': 'error',
        'Rad': 'wrong'
    })
    result = processor.prepare_sensor_row(row)
    
    assert 'timestamp' in result
    assert np.isnan(result['temperature'])
    assert np.isnan(result['humidity'])
    assert np.isnan(result['light'])

def test_prepare_form_data_valid(processor, valid_df):
    processor.gene_variety = "test_variety"
    row = valid_df.iloc[0]
    sensor_row = processor.prepare_sensor_row(row)
    result = processor.prepare_form_data(sensor_row)
    
    assert result['plant_name'] == 'plant1'
    assert result['gene_variety'] == 'test_variety'
    assert 'sensor_data' in result

def test_prepare_form_data_with_nan(processor, invalid_df):
    """Test form data preparation with NaN values"""
    row = invalid_df.iloc[1]
    sensor_row = processor.prepare_sensor_row(row)
    result = processor.prepare_form_data(sensor_row)
    
    assert result['plant_name'] == 'plant1'
    assert result['gene_variety'] == '11430'
    
    # Custom JSON encoder for NaN values
    class NaNEncoder(json.JSONEncoder):
        def default(self, obj):
            if pd.isna(obj):
                return None
            return super().default(obj)
    
    # Verify that NaN values are properly JSON serialized
    sensor_data = json.loads(result['sensor_data'])
    assert pd.isna(float(sensor_row['temperature']))  # Check original is NaN
    assert sensor_data['temperature'] is None  # Check JSON converts to null

def test_prepare_form_data_no_config(processor, valid_df):
    processor.gene_variety = None
    row = valid_df.iloc[0]
    sensor_row = processor.prepare_sensor_row(row)
    
    with pytest.raises(ValueError, match="Plant configuration not loaded"):
        processor.prepare_form_data(sensor_row)

def test_load_plant_config_missing_file(processor):
    processor.config_path = "/nonexistent/path"
    with pytest.raises(Exception):
        processor.load_plant_config()

def test_load_plant_config_invalid_plant(processor):
    processor.plant_name = "nonexistent_plant"
    with pytest.raises(ValueError, match="No configuration found for nonexistent_plant"):
        processor.load_plant_config() 