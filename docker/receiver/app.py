import os
import json
import datetime
import logging
from flask import Flask, request, jsonify
from pymongo import MongoClient
from gridfs import GridFS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MongoDB connection
try:
    client = MongoClient(os.getenv("MONGODB_URI", "mongodb://mongodb-service:27017/plant_data"))
    db = client.plant_data
    fs = GridFS(db)
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")

# Load genomic data
GENOMIC_DATA_PATH = os.getenv("GENOMIC_DATA_PATH", "/app/data/genomic_data")
try:
    logger.info(f"Attempting to read genomic data from: {GENOMIC_DATA_PATH}")
    if not os.path.exists(GENOMIC_DATA_PATH):
        logger.error(f"Genomic data file not found at: {GENOMIC_DATA_PATH}")
        raise FileNotFoundError(f"File not found: {GENOMIC_DATA_PATH}")
    
    with open(GENOMIC_DATA_PATH, "r") as f:
        content = f.read()
        logger.info(f"Raw genomic data content: {content}")
        
        # Parse the JSON content
        genomic_data_json = json.loads(content)
        if not isinstance(genomic_data_json, list):
            logger.error(f"Expected genomic data to be a list, got: {type(genomic_data_json)}")
            genomic_data_json = [genomic_data_json]
        
        # Create the mapping
        genomic_data = {str(item['VarietyID']): item for item in genomic_data_json}
        logger.info(f"Successfully parsed genomic data. Available varieties: {list(genomic_data.keys())}")
except Exception as e:
    logger.error(f"Error loading genomic data: {e}", exc_info=True)
    genomic_data = {}

@app.route("/receive_data", methods=["POST"])
def receive_data():
    try:
        logger.info("Received data request")
        logger.info(f"Form data: {request.form}")
        logger.info(f"Files: {list(request.files.keys())}")
        
        plant_name = request.form.get("plant_name")
        gene_variety = request.form.get("gene_variety")
        
        logger.info(f"Processing data for plant: {plant_name}, variety: {gene_variety}")
        logger.info(f"Available varieties in genomic data: {list(genomic_data.keys())}")
        
        if not plant_name:
            return jsonify({"status": "error", "message": "Missing plant_name"}), 400
        if not gene_variety:
            return jsonify({"status": "error", "message": "Missing gene_variety"}), 400

        sensor_data = request.form.get("sensor_data")
        if not sensor_data:
            return jsonify({"status": "error", "message": "Missing sensor_data"}), 400

        try:
            sensor_data_dict = json.loads(sensor_data)
            logger.info(f"Parsed sensor data: {sensor_data_dict}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid sensor_data JSON: {e}")
            return jsonify({"status": "error", "message": "Invalid sensor_data JSON"}), 400

        entry = {
            "timestamp": datetime.datetime.utcnow(),
            "plant_name": plant_name,
            "gene_variety": gene_variety,
            "sensor_data": sensor_data_dict
        }

        # Handle image
        if 'image' in request.files:
            image_file = request.files['image']
            logger.info(f"Processing image: {image_file.filename}")
            try:
                image_data = image_file.read()
                logger.info(f"Image size: {len(image_data)} bytes")
                image_id = fs.put(image_data, filename=image_file.filename)
                entry["image_id"] = image_id
                logger.info(f"Stored image with ID: {image_id}")
            except Exception as e:
                logger.error(f"Error storing image: {e}", exc_info=True)

        # Add genomic data
        if gene_variety in genomic_data:
            logger.info(f"Found genomic data for variety: {gene_variety}")
            entry["genomic_data"] = genomic_data[gene_variety]
            logger.info(f"Added genomic data: {genomic_data[gene_variety]}")
        else:
            logger.warning(f"No genomic data found for variety: {gene_variety}")
            logger.warning(f"Available varieties: {list(genomic_data.keys())}")

        # Store in MongoDB
        try:
            result = db.plant_data.insert_one(entry)
            logger.info(f"Stored entry with ID: {result.inserted_id}")
            return jsonify({"status": "success", "message": "Data stored"}), 200
        except Exception as e:
            logger.error(f"Error storing data in MongoDB: {e}", exc_info=True)
            return jsonify({"status": "error", "message": "Database error"}), 500

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    try:
        # Check MongoDB connection
        client.admin.command('ping')
        status = {
            "status": "healthy",
            "message": "Service is running",
            "genomic_data": {
                "loaded": len(genomic_data) > 0,
                "plants": list(genomic_data.keys())
            },
            "mongodb": "connected"
        }
        logger.info(f"Health check: {status}")
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "message": str(e)}), 500

if __name__ == "__main__":
    logger.info("Starting Flask application on port 5000...")
    app.run(host="0.0.0.0", port=5000)
