import os, time, requests, random
from glob import glob
import pandas as pd

"""
This script send plant image and its corresponding sensor data one by one.
It simulates random errors by 10% chance adding an empty row.
"""


default_plant_name = os.path.basename(os.getcwd())
PLANT_NAME = os.getenv("PLANT_NAME", "plant1")

RECEIVER_URL = os.getenv("RECEIVER_URL", "http://receiver-service:5000/receive_data")

image_files = sorted(glob(f"data/{PLANT_NAME}/images/*.png"))
sensor_file = f"data/{PLANT_NAME}/sensor_data.csv"

sensor_data = pd.read_csv("sensor_data.csv")

for i, image_file in enumerate(image_files):
    
    # Simulate random errors (10% chance)
    sensor_row = sensor_data.iloc[i % len(sensor_data)].to_dict()
    if random.random() < 0.1:
        sensor_row = {}

    with open(image_files, "rb") as img_file:
        files = {"image": (image_file, img_file, "image/png")}
        data = {"sensor_data": str(sensor_row), "plant_name": PLANT_NAME}

        try:
            response = requests.post(RECEIVER_URL, files=files, data=data)
            print(f"[{PLANT_NAME}] Sent: {image_file} | Status: {response.status_code}")
        except Exception as e:
            print(f"[{PLANT_NAME}] Failed to send {image_file}: {e}")

    time.sleep(10)
