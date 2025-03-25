import os, time, requests, random, json
from glob import glob
import pandas as pd
import logging
from plant_sender.core import PlantDataProcessor

"""
This script send plant image and its corresponding sensor data one by one.
It simulates random errors by 10% chance adding an empty row.
"""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_receiver(url: str, max_retries: int = 30, retry_interval: int = 10) -> bool:
    """Wait for receiver service to be ready"""
    for i in range(max_retries):
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 200:
                logger.info("Successfully connected to receiver")
                return True
        except:
            logger.info(f"Waiting for receiver service... ({i+1}/{max_retries})")
            time.sleep(retry_interval)
    return False

def main():
    # Get environment variables
    pod_name = os.getenv("PLANT_NAME", "plant-sender-0")
    plant_name = f"plant{int(pod_name.split('-')[-1]) + 1}"
    config_path = "/app/config/plant-configs"
    
    # Separate base URL and data endpoint
    receiver_base_url = "http://receiver-service:5000"
    receiver_data_url = f"{receiver_base_url}/receive_data"

    # Initialize processor
    processor = PlantDataProcessor(plant_name, config_path)
    try:
        processor.load_plant_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return

    # Setup paths
    sensor_file = f"/app/data/{plant_name}/sensor_data.csv"
    image_dir = f"/app/data/{plant_name}/images"
    os.makedirs(image_dir, exist_ok=True)

    # Wait for receiver using base URL
    if not wait_for_receiver(receiver_base_url):
        logger.error("Failed to connect to receiver service")
        return

    # Main processing loop
    try:
        sensor_data = pd.read_csv(sensor_file)
        if not processor.validate_sensor_data(sensor_data):
            return

        image_files = sorted(glob(f"{image_dir}/*.png"))
        
        while True:
            for i in range(len(sensor_data)):
                if random.random() < 0.1:
                    sensor_row = {}
                else:
                    sensor_row = processor.prepare_sensor_row(sensor_data.iloc[i])

                form_data = processor.prepare_form_data(sensor_row)
                
                # Handle image upload
                files = {}
                if image_files and i < len(image_files):
                    try:
                        with open(image_files[i], 'rb') as f:
                            files['image'] = (os.path.basename(image_files[i]), f, 'image/png')
                            response = requests.post(receiver_data_url, data=form_data, files=files, timeout=10)
                            logger.info(f"Response status: {response.status_code}")
                    except Exception as e:
                        logger.error(f"Failed to send data: {e}")

                time.sleep(10)

    except Exception as e:
        logger.error(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()
