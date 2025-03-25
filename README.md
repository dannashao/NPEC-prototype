# Plant Monitoring System

A Kubernetes-based system for monitoring plant sensor data and images, with genomic data integration.

## System Architecture

The system consists of the following components:
- **Plant Sender**: Sends sensor data and plant images
- **Receiver**: REST API service that processes incoming data
- **MongoDB**: Database for storing sensor data, images, and genomic information
- **MongoDB Express**: Web-based MongoDB admin interface

## Prerequisites

- Docker
- Kubernetes (kind or minikube)
- kubectl

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd plant-monitoring-system
```

2. Prepare your data directory:
   - Create a `data` directory in the project root:
     ```bash
     mkdir data
     ```
   - Place your data with the following structure:
     ```
     data/
     ├── plant1/
     │   ├── images/
     │   │   ├── image1.png
     │   │   └── ...
     │   └── sensor_data.csv
     ├── plant2/
     │   ├── images/
     │   │   ├── image1.png
     │   │   └── ...
     │   └── sensor_data.csv
     └── genomic_data.json
     ```

3. Setup the cluster:
```bash
./scripts/setup.sh
```

4. Deploy the system:
```bash
./scripts/deploy.sh
```

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

### Image Storage
Images are stored using MongoDB's GridFS system:
- Images are split into chunks for efficient storage
- Each image is referenced by an `image_id` in the plant data
- Images can be accessed through MongoDB Express or the MongoDB shell

#### Accessing Images
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

## Configuration

### Environment Variables

Plant Sender:
- `PLANT_NAME`: Name of the plant (default: "plant1")
- `GENE_VARIETY`: Genetic variety ID (default: "11430")
- `RECEIVER_URL`: URL of the receiver service

Receiver:
- `MONGODB_URI`: MongoDB connection string
- `GENOMIC_DATA_PATH`: Path to genomic data file

MongoDB Express:
- `ME_CONFIG_BASICAUTH_USERNAME`: Admin username (default: "admin")
- `ME_CONFIG_BASICAUTH_PASSWORD`: Admin password (default: "pass")

### ConfigMaps

#### Genomic Data ConfigMap
The system uses a ConfigMap to store genomic data for different plant varieties:

1. Create the ConfigMap from JSON file:
```bash
kubectl create configmap genomic-data --from-file=genomic_data=data/genomic_data.json
```

2. Verify the ConfigMap contents:
```bash
# View all variety IDs
kubectl get configmap genomic-data -o jsonpath='{.data.genomic_data}' | jq '.[].VarietyID'

# Expected output:
"11430"
"A3"
"A310"
```

3. View full genomic data:
```bash
kubectl get configmap genomic-data -o jsonpath='{.data.genomic_data}' | jq '.'
```

## Access Points

### API Endpoints
- `POST /receive_data`: Receives plant data and images
- `GET /health`: Health check endpoint

### MongoDB Express Interface
- URL: `http://plant-data.local/mongo-express`
- Credentials:
  - Username: admin
  - Password: pass
- Features:
  - Browse and query collections
  - View stored sensor data and images
  - Monitor database status
  - Manage database operations

## Monitoring

Common monitoring commands:
```bash
# View system status
kubectl get pods

# Check component logs
kubectl logs -l app=plant-sender
kubectl logs -l app=receiver
kubectl logs -l app=mongo-express

# View services
kubectl get services
```

## Troubleshooting

If you encounter issues:
1. Check pod status: `kubectl get pods`
2. View application logs: `kubectl logs -l app=<component-name>`
3. Ensure all prerequisites are installed
4. Verify network connectivity: `kubectl get ingress`
5. Check MongoDB Express access at `/mongo-express`

## Cleanup

Remove all resources:
```bash
kind delete cluster --name plant-cluster
```

## Data Structure

1. **Data Directory Structure**:
   ```
   data/
   ├── plant1/
   │   ├── images/
   │   │   ├── image1.png
   │   │   └── ...
   │   └── sensor_data.csv
   ├── plant2/
   │   ├── images/
   │   │   ├── image1.png
   │   │   └── ...
   │   └── sensor_data.csv
   └── genomic_data.json
   ```

2. **Data Organization**:
   - Each plant has its own directory (`plant1`, `plant2`, etc.)
   - Plant images are stored in the `images` subdirectory
   - Sensor data is stored in `sensor_data.csv` within each plant directory
   - Genomic data is stored in the root of the data directory

3. **Mounting Configuration**:
   - The data directory is mounted into the kind cluster at `/data`
   - The plant-sender pod accesses data through `/app/data`
   - Directory structure must match the expected format