# Monitoring and Validation

## Real-Time Validation API

The system provides a real-time validation API to check data status and quality.

### Validation Endpoints

#### Single Plant Validation
```bash
curl "http://plant-data.local/validate?plant_name=plant1"
```

Response:
```json
{
    "plant_name": "plant1",
    "status": "valid",
    "last_received": "2024-03-25T12:40:00Z",
    "errors": [],
    "sensor_data": {
        "temperature": 22.5,
        "humidity": 65.0,
        "light": 800.0
    },
    "recent_error_rate": "10.0%",
    "gene_variety": "11430",
    "validation_timestamp": "2024-03-25T12:40:05Z"
}
```

#### System-Wide Validation
```bash
curl "http://plant-data.local/validate/system"
```

Response:
```json
{
    "timestamp": "2024-03-25T12:40:00Z",
    "total_plants": 2,
    "plants": {
        "plant1": { ... },
        "plant2": { ... }
    },
    "system_stats": {
        "total_logs": 1000,
        "error_rate": "5.0%",
        "active_plants": 2
    }
}
```

## Monitoring Tools

### Component Health Checks
```bash
# Check receiver health
curl "http://plant-data.local/health"

# View validation logs
kubectl logs -l app=receiver | grep "validation"

# Monitor error rates
kubectl logs -l app=receiver | grep "ERROR"
```

### Data Quality Monitoring
- Recent error rates by plant
- Data validation status
- Last received timestamps
- Sensor value ranges

### System Metrics
- Active plants count
- Total processed records
- System-wide error rate
- Component health status 