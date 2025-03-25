import pytest
import pandas as pd
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
    return PlantDataProcessor("plant1", sample_config)

def test_load_plant_config(processor, sample_config):
    config = processor.load_plant_config()
    assert config["gene_variety"] == "11430"
    assert processor.gene_variety == "11430"

def test_load_plant_config_invalid_plant(sample_config):
    processor = PlantDataProcessor("invalid_plant", sample_config)
    with pytest.raises(ValueError):
        processor.load_plant_config()

def test_validate_sensor_data(processor, sample_sensor_data):
    assert processor.validate_sensor_data(sample_sensor_data) == True

def test_validate_sensor_data_missing_columns(processor):
    invalid_data = pd.DataFrame({
        'Temperature': [20.5],  # Wrong column name
        'RHmean.air': [65.0],
        'Rad': [800.0]
    })
    assert processor.validate_sensor_data(invalid_data) == False

def test_prepare_sensor_row(processor, sample_sensor_data):
    row = processor.prepare_sensor_row(sample_sensor_data.iloc[0])
    assert isinstance(row['timestamp'], str)
    assert row['temperature'] == 20.5
    assert row['humidity'] == 65.0
    assert row['light'] == 800.0

def test_prepare_form_data(processor):
    processor.load_plant_config()
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
    sensor_row = {
        'timestamp': '2024-03-25T10:00:00',
        'temperature': 20.5,
        'humidity': 65.0,
        'light': 800.0
    }
    with pytest.raises(ValueError):
        processor.prepare_form_data(sensor_row) 