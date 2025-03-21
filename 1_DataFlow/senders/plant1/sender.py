import os
import time
import random
import requests
import pandas as pd

"""
This script send plant image and its corresponding sensor data one by one.
It simulates random errors by 10% chance adding an empty row.
"""


# Directory name as default PLANT_NAME
default_plant_name = os.path.basename(os.getcwd())
PLANT_NAME = os.getenv("PLANT_NAME", default_plant_name)

RECEIVER_URL = "http://receiver:5000/receive_data"

sensor_data = pd.read_csv("sensor_data.csv")
image_folder = "images"
image_files = sorted(os.listdir(image_folder))

for i, image_file in enumerate(image_files):
    image_path = os.path.join(image_folder, image_file)
    
    # Simulate random errors (10% chance)
    sensor_row = sensor_data.iloc[i % len(sensor_data)].to_dict()
    if random.random() < 0.1:
        sensor_row = {}

    with open(image_path, "rb") as img_file:
        files = {"image": (image_file, img_file, "image/png")}
        data = {"sensor_data": str(sensor_row), "plant_name": PLANT_NAME}

        try:
            response = requests.post(RECEIVER_URL, files=files, data=data)
            print(f"[{PLANT_NAME}] Sent: {image_file} | Status: {response.status_code}")
        except Exception as e:
            print(f"[{PLANT_NAME}] Failed to send {image_file}: {e}")

    time.sleep(5)
