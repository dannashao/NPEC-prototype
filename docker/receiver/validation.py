from typing import Dict, Any, Tuple, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataValidator:
    REQUIRED_SENSOR_FIELDS = {'temperature', 'humidity', 'light'}
    VALID_VALUE_RANGES = {
        'temperature': (-10, 50),  # °C
        'humidity': (0, 100),      # %
        'light': (0, 2000)         # µmol/m²/s
    }

    @staticmethod
    def validate_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate incoming data structure and values"""
        errors = []

        # Required fields check
        if not data.get('plant_name'):
            errors.append("Missing plant_name")
        if not data.get('gene_variety'):
            errors.append("Missing gene_variety")

        # Validate sensor data
        try:
            sensor_data = data.get('sensor_data', {})
            if isinstance(sensor_data, str):
                import json
                sensor_data = json.loads(sensor_data)

            # Check required sensor fields
            missing_fields = DataValidator.REQUIRED_SENSOR_FIELDS - set(sensor_data.keys())
            if missing_fields:
                errors.append(f"Missing sensor fields: {', '.join(missing_fields)}")

            # Validate value ranges
            for field, (min_val, max_val) in DataValidator.VALID_VALUE_RANGES.items():
                value = sensor_data.get(field)
                if value is not None:
                    try:
                        value = float(value)
                        if not min_val <= value <= max_val:
                            errors.append(f"{field} value {value} outside valid range [{min_val}, {max_val}]")
                    except ValueError:
                        errors.append(f"Invalid {field} value: {value}")

            # Timestamp validation
            timestamp = sensor_data.get('timestamp')
            if not timestamp:
                errors.append("Missing timestamp")
            else:
                try:
                    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    errors.append(f"Invalid timestamp format: {timestamp}")

        except Exception as e:
            errors.append(f"Error parsing sensor data: {str(e)}")

        return len(errors) == 0, errors

class DataLogger:
    def __init__(self, db):
        self.db = db
        self.logs_collection = db.data_logs

    def log_data(self, data: Dict[str, Any], is_valid: bool, errors: List[str]) -> str:
        """Log data with validation status and errors"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "plant_name": data.get("plant_name"),
            "gene_variety": data.get("gene_variety"),
            "sensor_data": data.get("sensor_data"),
            "status": "valid" if is_valid else "invalid",
            "errors": errors,
            "raw_data": data  # Store original data for debugging
        }

        result = self.logs_collection.insert_one(log_entry)
        
        # Log severe errors
        if not is_valid:
            logger.error(f"Data validation failed for plant {data.get('plant_name')}: {errors}")

        return str(result.inserted_id)

    def get_plant_status(self, plant_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent logs for a specific plant"""
        return list(self.logs_collection
                   .find({"plant_name": plant_name})
                   .sort("timestamp", -1)
                   .limit(limit))

    def get_validation_status(self, plant_name: str) -> Dict[str, Any]:
        """Get real-time validation status for a plant"""
        try:
            # Get the most recent log entry
            latest_log = self.logs_collection.find_one(
                {"plant_name": plant_name},
                sort=[("timestamp", -1)]
            )

            if not latest_log:
                return {
                    "plant_name": plant_name,
                    "status": "unknown",
                    "last_received": None,
                    "errors": ["No data received yet"],
                    "sensor_data": None
                }

            # Get error statistics from recent logs
            recent_logs = self.logs_collection.find(
                {"plant_name": plant_name},
                sort=[("timestamp", -1)],
                limit=10
            )

            error_count = sum(1 for log in recent_logs if log.get("status") == "invalid")
            
            return {
                "plant_name": plant_name,
                "status": latest_log.get("status", "unknown"),
                "last_received": latest_log.get("timestamp"),
                "errors": latest_log.get("errors", []),
                "sensor_data": latest_log.get("sensor_data"),
                "recent_error_rate": f"{error_count/10:.1%}",
                "gene_variety": latest_log.get("gene_variety"),
                "validation_timestamp": datetime.utcnow().isoformat() + "Z"
            }

        except Exception as e:
            logger.error(f"Error getting validation status for {plant_name}: {e}")
            return {
                "plant_name": plant_name,
                "status": "error",
                "last_received": None,
                "errors": [str(e)],
                "validation_timestamp": datetime.utcnow().isoformat() + "Z"
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system validation status"""
        try:
            # Get unique plant names
            plant_names = self.logs_collection.distinct("plant_name")
            
            # Get status for each plant
            plant_statuses = {}
            for plant in plant_names:
                plant_statuses[plant] = self.get_validation_status(plant)

            # Calculate system-wide statistics
            total_logs = self.logs_collection.count_documents({})
            error_logs = self.logs_collection.count_documents({"status": "invalid"})
            
            return {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "total_plants": len(plant_names),
                "plants": plant_statuses,
                "system_stats": {
                    "total_logs": total_logs,
                    "error_rate": f"{error_logs/total_logs:.1%}" if total_logs > 0 else "0%",
                    "active_plants": len(plant_names)
                }
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "status": "error",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "error": str(e)
            } 