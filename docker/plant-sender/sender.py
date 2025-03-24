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
sensor_file = f"/app/data/{PLANT_NAME}/sensor_data.csv"
image_dir = f"/app/data/{PLANT_NAME}/images"

# Ensure image directory exists
os.makedirs(image_dir, exist_ok=True)

# Add debug logging
logger.info(f"Image directory path: {image_dir}")
logger.info("Listing /app/data contents:")
try:
    logger.info(str(os.listdir("/app/data")))
    if os.path.exists(f"/app/data/{PLANT_NAME}"):
        logger.info(f"Listing plant directory contents:")
        logger.info(str(os.listdir(f"/app/data/{PLANT_NAME}")))
except Exception as e:
    logger.error(f"Error listing directories: {e}")

# Get list of images
image_files = sorted(glob(f"{image_dir}/*.png"))
logger.info(f"Found {len(image_files)} image files in {image_dir}")
if len(image_files) == 0:
    logger.warning(f"No image files found. Contents of parent directory:")
    try:
        parent_dir = os.path.dirname(image_dir)
        logger.warning(f"Parent directory ({parent_dir}) contents: {os.listdir(parent_dir)}")
        if os.path.exists(image_dir):
            logger.warning(f"Target directory ({image_dir}) contents: {os.listdir(image_dir)}")
    except Exception as e:
        logger.error(f"Error listing directory: {e}")

def validate_sensor_data(df):
    """Validate sensor data CSV structure"""
    required_columns = {'Tmean.air', 'RHmean.air', 'Rad'}  # Update required columns
    missing_columns = required_columns - set(df.columns)
    
    if missing_columns:
        logger.error(f"Missing required columns in sensor data: {missing_columns}")
        logger.error(f"Available columns: {df.columns.tolist()}")
        return False
    return True

# Wait for receiver to be ready
def wait_for_receiver():
    max_retries = 30
    retry_interval = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"http://receiver-service:5000/health")
            if response.status_code == 200:
                logger.info("Successfully connected to receiver")
                return True
        except:
            logger.info(f"Waiting for receiver service... ({i+1}/{max_retries})")
            time.sleep(retry_interval)
    return False

if not wait_for_receiver():
    logger.error("Failed to connect to receiver service")
    exit(1)

# Read sensor data
try:
    sensor_data = pd.read_csv(sensor_file)
    logger.info(f"Successfully loaded sensor data from {sensor_file}")
    logger.info(f"CSV columns: {sensor_data.columns.tolist()}")
    
    if not validate_sensor_data(sensor_data):
        logger.error("Invalid sensor data structure")
        exit(1)
        
    logger.info(f"First row of data: {sensor_data.iloc[0].to_dict()}")
except Exception as e:
    logger.error(f"Error loading sensor data: {e}")
    exit(1)

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
                'timestamp': pd.Timestamp.now().isoformat(),
                'temperature': float(row['Tmean.air']),
                'humidity': float(row['RHmean.air']),
                'light': float(row['Rad'])
            }

        # Prepare the multipart form data
        form_data = {
            'plant_name': PLANT_NAME,
            'gene_variety': GENE_VARIETY,
            'sensor_data': json.dumps(sensor_row)
        }

        # Prepare files if available
        files = {}
        if image_files and i < len(image_files):
            image_path = image_files[i]
            logger.info(f"Preparing to send image: {image_path}")
            try:
                files['image'] = (
                    os.path.basename(image_path),
                    open(image_path, 'rb'),
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
