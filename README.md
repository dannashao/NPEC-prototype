# Plant Monitoring System

A Kubernetes-based system for monitoring plant sensor data and images, with genomic data integration.

## Quick Links
- [Data Structure Guide](docs/data-structure.md)
- [StatefulSet Configuration](docs/statefulset.md)
- [Storage Configuration](docs/storage.md)
- [Monitoring and Validation](docs/monitoring.md)

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
git clone <https://github.com/dannashao/NPEC-prototype.git>
cd plant-monitoring-system
```

2. Prepare your data directory structure (see [Data Structure Guide](docs/data-structure.md))

3. Setup the cluster:
```bash
./scripts/setup.sh
```

4. Deploy the system:

**WARNING: This script deletes all existing resources. Use it only for the first time deployment or system reset.**

```bash
./scripts/deploy.sh
```

## Access Points

### API Endpoints
- `POST /receive_data`: Receives plant data and images
- `GET /health`: Health check endpoint
- `GET /validate`: Real-time data validation status
- `GET /validate/system`: System-wide validation status

### MongoDB Express Interface
- URL: `http://plant-data.local/mongo-express`
- Credentials: admin/pass

## Basic Monitoring
```bash
# View system status
kubectl get pods

# Check validation status
curl "http://plant-data.local/validate/system"

# View recent logs
kubectl logs -l app=receiver --tail=100
```

See [Monitoring and Validation](docs/monitoring.md) for detailed monitoring information.

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


## StatefulSet Configuration

The plant sender uses a StatefulSet to manage multiple plant monitoring instances:

### Pod Naming Convention
- Pods are named sequentially: `plant-sender-0`, `plant-sender-1`, etc.
- Each pod automatically maps to a corresponding plant: 
  - `plant-sender-0` → `plant1`
  - `plant-sender-1` → `plant2`

### Scaling Plants
```bash
# View current plant sender pods
kubectl get pods -l app=plant-sender

# Scale to monitor more plants
kubectl scale statefulset plant-sender --replicas=3

# Scale down if needed
kubectl scale statefulset plant-sender --replicas=1
```

### Volume Mounts
The StatefulSet configuration includes:
- Plant data volume: `/app/data`
- Configuration volume: `/app/config`

### Environment Variables
Each pod automatically gets:
- `PLANT_NAME`: Set from pod name (e.g., "plant-sender-0")
- `RECEIVER_URL`: Points to receiver service

### Monitoring StatefulSet
```bash
# Check StatefulSet status
kubectl get statefulset plant-sender

# View individual pod logs
kubectl logs plant-sender-0
kubectl logs plant-sender-1

# Check pod details
kubectl describe pod plant-sender-0
```

### Troubleshooting StatefulSet
1. Ensure data directories exist for each plant
2. Verify ConfigMaps are properly mounted
3. Check individual pod logs for specific plant issues
4. Verify pod naming matches plant data structure

## Storage Configuration

The system uses three types of persistent storage:

1. MongoDB Storage (`mongodb-storage.yml`):
   - Stores the MongoDB database
   - 1GB capacity
   - ReadWriteOnce access mode

2. Image Storage (`image-storage.yml`):
   - Stores plant images
   - Mounted to both sender and receiver

3. ConfigMap Storage:
   - Genomic data
   - Plant configurations
   - Sensor data templates