# Data Structure Guide

## Data Model

### Plant Identification
The system uses a two-level identification system:
- `plant_name`: Identifies individual plants (e.g., "plant1", "plant2")
- `gene_variety`: Links plants to their genetic variety (e.g., "11430")

### Data Components
Each plant entry contains:
- Plant Name and Gene Variety
- Sensor Data (temperature, humidity, light)
- Images (stored in GridFS, referenced by `image_id`)
- Genomic Data (linked via Gene Variety)

## Directory Structure
   ```
    data/
    ├── plant1/
    │ ├── images/
    │ │ ├── image1.png
    │ │ └── ...
    │ └── sensor_data.csv
    ├── plant2/
    │ ├── images/
    │ │ ├── image1.png
    │ │ └── ...
    │ └── sensor_data.csv
    └── genomic_data.json
   ```

## Data Organization
- Each plant has its own directory (`plant1`, `plant2`, etc.)
- Plant images are stored in the `images` subdirectory
- Sensor data is stored in `sensor_data.csv` within each plant directory
- Genomic data is stored in the root of the data directory

## Image Storage
Images are stored using MongoDB's GridFS system:
- Images are split into chunks for efficient storage
- Each image is referenced by an `image_id` in the plant data
- Images can be accessed through MongoDB Express or the MongoDB shell

### Accessing Images
Through MongoDB Express:
1. Navigate to `http://plant-data.local/mongo-express`
2. Go to the `plant_data` database
3. Look for the `fs.files` and `fs.chunks` collections
4. Images can be found in `fs.files` with their metadata
5. The actual image data is stored in `fs.chunks`

Through MongoDB Shell:
```bash
# Connect to MongoDB
kubectl exec -it $(kubectl get pod -l app=mongodb -o jsonpath='{.items[0].metadata.name}') -- mongosh

# Switch to plant_data database
use plant_data

# Find image metadata by ID
db.fs.files.find({"_id": ObjectId("YOUR_IMAGE_ID")})

# Export image (from your local machine)
kubectl exec -it $(kubectl get pod -l app=mongodb -o jsonpath='{.items[0].metadata.name}') -- mongofiles --db=plant_data get_id 'YOUR_IMAGE_ID' --local=downloaded_image.jpg
```

## Mounting Configuration
- The data directory is mounted into the kind cluster at `/data`
- The plant-sender pod accesses data through `/app/data`
- Directory structure must match the expected format