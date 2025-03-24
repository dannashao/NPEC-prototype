import os, time, requests, random, json
from glob import glob
import pandas as pd
import logging

"""
This script send plant image and its corresponding sensor data one by one.
It simulates random errors by 10% chance adding an empty row.
"""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PLANT_NAME = os.getenv("PLANT_NAME", "plant1")
GENE_VARIETY = os.getenv("GENE_VARIETY", "11430")  # This should match VarietyID in genomic data
RECEIVER_URL = os.getenv("RECEIVER_URL", "http://receiver-service:5000/receive_data")

# Update paths for both sensor data and images
sensor_file = f"/app/data/{PLANT_NAME}.sensor_data.csv"
image_dir = f"/app/images/{PLANT_NAME}"

# Ensure image directory exists
os.makedirs(image_dir, exist_ok=True)

def wait_for_receiver():
    max_retries = 30
    retry_interval = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"http://receiver-service:5000/health")
            if response.status_code == 200:
                print("Successfully connected to receiver")
                return True
        except:
            print(f"Waiting for receiver service... ({i+1}/{max_retries})")
            time.sleep(retry_interval)
    return False

# Wait for receiver to be ready
if not wait_for_receiver():
    print("Failed to connect to receiver service")
    exit(1)

# Read sensor data
try:
    sensor_data = pd.read_csv(sensor_file)
    print(f"Successfully loaded sensor data from {sensor_file}")
except Exception as e:
    print(f"Error loading sensor data: {e}")
    exit(1)

# Get list of images
image_files = sorted(glob(f"{image_dir}/*.png"))
print(f"Found {len(image_files)} image files in {image_dir}")

while True:
    for i in range(len(sensor_data)):
        logger.info(f"Processing row {i}")
        
        # Verify sensor data file exists
        if not os.path.exists(sensor_file):
            logger.error(f"Sensor data file not found: {sensor_file}")
            time.sleep(10)
            continue

        # Verify image directory
        logger.info(f"Checking image directory: {image_dir}")
        if not os.path.exists(image_dir):
            logger.warning(f"Image directory not found: {image_dir}")

        # Prepare sensor data
        if random.random() < 0.1:
            sensor_row = {}
        else:
            row = sensor_data.iloc[i]
            sensor_row = {
                'timestamp': row['timestamp'],
                'temperature': float(row['temperature']),
                'humidity': float(row['humidity']),
                'light': float(row['light'])
            }

        # Prepare the multipart form data
        form_data = {
            'plant_name': PLANT_NAME,
            'gene_variety': GENE_VARIETY,
            'sensor_data': json.dumps(sensor_row)
        }

        # Prepare files if available
        files = {}
        image_path = None
        if image_files and i < len(image_files):
            image_path = image_files[i]
            logger.info(f"Preparing to send image: {image_path}")
            try:
                # Move the file opening into the request context
                files['image'] = (
                    os.path.basename(image_path),
                    open(image_path, 'rb'),  # Don't close the file here
                    'image/png'
                )
                logger.info(f"Successfully prepared image: {image_path}")
                
                # Send the request with the open file
                response = requests.post(
                    RECEIVER_URL,
                    data=form_data,
                    files=files,
                    timeout=10
                )
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response content: {response.text}")
                
            except Exception as e:
                logger.error(f"Failed to send data: {e}", exc_info=True)
            finally:
                # Clean up: close the file if it was opened
                if 'image' in files:
                    files['image'][1].close()

        time.sleep(10)
