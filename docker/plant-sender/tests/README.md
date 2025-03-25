# Plant Sender Tests

This directory contains the test suite for the Plant Sender application. The tests use pytest framework to verify the functionality of the data processing and validation components.

## Test Structure

- `test_core.py`: Tests for the PlantDataProcessor class functionality
  - Data validation
  - Sensor data processing
  - Form data preparation
  - Configuration loading
  - NaN value handling
  - JSON serialization

## Key Test Fixtures

### `processor`
Base PlantDataProcessor instance with sample configuration loaded.
```python
@pytest.fixture
def processor(sample_config):
    proc = PlantDataProcessor("plant1", sample_config)
    proc.load_plant_config()
    return proc
```

### `sample_config`
Temporary configuration file with test data.
```python
@pytest.fixture
def sample_config(tmp_path):
    config = {
        "plant1": {
            "gene_variety": "11430"
        }
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config))
    return str(config_file)
```

### `valid_df` and `invalid_df`
Sample DataFrames for testing sensor data processing.
```python
@pytest.fixture
def valid_df():
    return pd.DataFrame({
        'Tmean.air': [20.5, 21.0],
        'RHmean.air': [65.0, 67.0],
        'Rad': [800, 850]
    })
```

## Running Tests

From the project root directory:
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=plant_sender

# Run specific test file
pytest tests/test_core.py

# Run tests with detailed output
pytest -v

# Run tests and show print statements
pytest -s
```

## Test Categories

### Configuration Tests
- Loading valid configurations
- Handling missing configurations
- Invalid plant names
- File access errors

### Data Validation Tests
- Valid sensor data
- Missing columns
- Empty DataFrames
- NaN values
- Invalid data types

### Data Processing Tests
- Sensor row preparation
- Form data preparation
- JSON serialization
- NaN handling
- Float precision

### Error Handling Tests
- Missing configurations
- Invalid data formats
- Type conversion errors
- File access errors

## Adding New Tests

When adding new tests:

1. Follow the existing naming convention: `test_<functionality>_<scenario>`
2. Add appropriate docstrings explaining the test purpose
3. Use fixtures when possible to reduce code duplication
4. Include both positive and negative test cases
5. Add error handling tests for edge cases

## Test Data Guidelines

- Use realistic but simplified data values
- Include edge cases (NaN, empty values, etc.)
- Keep test data minimal but sufficient
- Use fixtures for reusable test data

## Common Testing Patterns

```python
# Testing valid scenarios
def test_valid_scenario(processor):
    result = processor.some_method()
    assert result.expected_value == actual_value

# Testing error cases
def test_error_scenario(processor):
    with pytest.raises(ValueError):
        processor.some_method()

# Testing with invalid data
def test_invalid_data(processor):
    result = processor.process_data(invalid_input)
    assert result.status == "error"
```

## Maintenance

- Keep tests up to date with code changes
- Regularly run coverage reports
- Review and update test data as needed
- Document any special test requirements 