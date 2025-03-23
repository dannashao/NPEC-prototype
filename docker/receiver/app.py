 import os
import json
import datetime
from flask import Flask, request, jsonify
from pymongo import MongoClient
from gridfs import GridFS

app = Flask(__name__)
client = MongoClient("mongodb://mongo:27017/")
db = client["phenotyping_db"]
fs = GridFS(db)

# Load genomic data
GENOMIC_DATA_FILE = "data/genomic_data.json"
if os.path.exists(GENOMIC_DATA_FILE):
    with open(GENOMIC_DATA_FILE, "r") as f:
        genomic_data_json = json.load(f)
        genomic_data = {}
        for item in genomic_data_json:
           name = item['plant_name']
           genomic_data[name] = item
else:
    genomic_data = {}


@app.route("/receive_data", methods=["POST"])
def receive_data():
    plant_name = request.form.get("plant_name")
    image_file = request.files.get("image")
    sensor_data = request.form.get("sensor_data")

    if not image_file or not sensor_data:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    image_id = fs.put(image_file.read(), filename=image_file.filename)

    # Check if plant exists; if not, prompt user for genomic data
    if plant_name not in genomic_data:
        print(f"New plant detected: {plant_name}")
        genomic_data[plant_name] = input(f"Enter genomic data for {plant_name}: ")
        with open(GENOMIC_DATA_FILE, "w") as f:
            json.dump(genomic_data, f)

    entry = {
        "timestamp": datetime.datetime.utcnow(),
        "plant_name": plant_name,
        "image_id": image_id,
        "sensor_data": json.loads(sensor_data),
        "genomic_data": genomic_data[plant_name]
    }
    db.phenotyping_data.insert_one(entry)

    return jsonify({"status": "success", "message": "Data stored"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
