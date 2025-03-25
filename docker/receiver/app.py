import os
import json
import logging
from flask import Flask, request, jsonify
from pymongo import MongoClient
from gridfs import GridFS
from validation import DataValidator, DataLogger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MongoDB connection
try:
    client = MongoClient(os.getenv("MONGODB_URI", "mongodb://mongodb-service:27017/plant_data"))
    db = client.plant_data
    fs = GridFS(db)
    data_logger = DataLogger(db)
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")

# Load genomic data
GENOMIC_DATA_PATH = os.getenv("GENOMIC_DATA_PATH", "/app/data/genomic_data")
try:
    with open(GENOMIC_DATA_PATH, "r") as f:
        genomic_data = json.load(f)
        if not isinstance(genomic_data, list):
            genomic_data = [genomic_data]
        genomic_data = {str(item['VarietyID']): item for item in genomic_data}
        logger.info(f"Successfully loaded genomic data for varieties: {list(genomic_data.keys())}")
except Exception as e:
    logger.error(f"Error loading genomic data: {e}", exc_info=True)
    genomic_data = {}

@app.route("/receive_data", methods=["POST"])
def receive_data():
    try:
        # Extract data
        plant_name = request.form.get("plant_name")
        gene_variety = request.form.get("gene_variety")
        sensor_data = request.form.get("sensor_data", "{}")

        data = {
            "plant_name": plant_name,
            "gene_variety": gene_variety,
            "sensor_data": json.loads(sensor_data) if isinstance(sensor_data, str) else sensor_data
        }

        # Validate data
        is_valid, errors = DataValidator.validate_data(data)

        # Log the data
        log_id = data_logger.log_data(data, is_valid, errors)

        # Process valid data
        if is_valid:
            # Handle image if present
            if 'image' in request.files:
                image_file = request.files['image']
                image_id = fs.put(image_file.read(), filename=image_file.filename)
                data["image_id"] = image_id

            # Add genomic data
            if gene_variety in genomic_data:
                data["genomic_data"] = genomic_data[gene_variety]
            else:
                logger.warning(f"No genomic data found for variety: {gene_variety}")

            # Store valid data in main collection
            db.plant_data.insert_one(data)
            
            return jsonify({
                "status": "success",
                "message": "Data stored successfully",
                "log_id": log_id
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Data validation failed",
                "errors": errors,
                "log_id": log_id
            }), 400

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/plant_status/<plant_name>", methods=["GET"])
def get_plant_status(plant_name):
    """Get recent logs for a specific plant"""
    try:
        logs = data_logger.get_plant_status(plant_name)
        return jsonify({
            "status": "success",
            "plant_name": plant_name,
            "logs": logs
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving plant status: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/health", methods=["GET"])
def health_check():
    try:
        client.admin.command('ping')
        return jsonify({
            "status": "healthy",
            "message": "Service is running",
            "genomic_data": {
                "loaded": len(genomic_data) > 0,
                "varieties": list(genomic_data.keys())
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "message": str(e)
        }), 500

@app.route("/validate", methods=["GET"])
def validate_status():
    """Get validation status for a specific plant or all plants"""
    try:
        plant_name = request.args.get("plant_name")
        
        if plant_name:
            # Get status for specific plant
            status = data_logger.get_validation_status(plant_name)
            return jsonify(status), 200
        else:
            # Get system-wide status
            status = data_logger.get_system_status()
            return jsonify(status), 200

    except Exception as e:
        logger.error(f"Error in validation endpoint: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/validate/system", methods=["GET"])
def system_status():
    """Get system-wide validation status"""
    try:
        status = data_logger.get_system_status()
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error in system status endpoint: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
