from flask import Flask, render_template, request, jsonify, flash, Blueprint
from pymongo import MongoClient
import logging
from src.models.miappe_schema import MIAPPESchema
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this in production

# Create a Blueprint with url_prefix and static folder
miappe_bp = Blueprint('miappe', __name__, 
                     url_prefix='/miappe',
                     static_folder='static',
                     template_folder='templates')

# MongoDB connection
try:
    client = MongoClient("mongodb://mongodb-service:27017/plant_data")
    db = client.plant_data
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")

# Load MIAPPE schema
schema = MIAPPESchema()
schema.load_from_csv("/app/src/models/MIAPPE_Checklist_Data_Model_with_Requirements.csv")

@miappe_bp.route('/')
def index():
    # Get MongoDB columns
    try:
        sample_doc = db.plant_data.find_one()
        mongo_fields = list(sample_doc.keys()) if sample_doc else []
        mongo_fields = [f for f in mongo_fields if f != '_id']
    except Exception as e:
        logger.error(f"Failed to fetch MongoDB fields: {e}")
        mongo_fields = []

    return render_template(
        'index.html',
        scopes=schema.scopes,
        mongo_fields=mongo_fields
    )

@miappe_bp.route('/save_checklist', methods=['POST'])
def save_checklist():
    data = request.json
    
    # Validate mandatory fields
    errors = []
    for scope_name, scope_data in data.items():
        if schema.scopes[scope_name].requirement == 0:  # Mandatory scope
            scope_errors = schema.validate_scope(scope_name, scope_data)
            errors.extend(scope_errors)
    
    # For now, just return validation results
    # Later we'll add PostgreSQL storage
    return jsonify({
        'success': len(errors) == 0,
        'errors': errors,
        'is_complete': len(errors) == 0
    })

@miappe_bp.route('/health')
def health():
    return jsonify({'status': 'healthy'})

# Register the blueprint
app.register_blueprint(miappe_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001) 