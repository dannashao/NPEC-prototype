# Storage Configuration

## Storage Types

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

## ConfigMaps

### Genomic Data ConfigMap
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
```

3. Update monitoring.md to include troubleshooting:

```markdown:docs/monitoring.md
# Monitoring and Validation

[... existing monitoring content ...]

## Troubleshooting

If you encounter issues:
1. Check pod status: `kubectl get pods`
2. View application logs: `kubectl logs -l app=<component-name>`
3. Ensure all prerequisites are installed
4. Verify network connectivity: `kubectl get ingress`
5. Check MongoDB Express access at `/mongo-express`

## Environment Variables

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
```

4. Update the main README.md to be more concise:

```markdown:README.md
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
git clone <repository-url>
cd plant-monitoring-system
```

2. Prepare your data directory structure (see [Data Structure Guide](docs/data-structure.md))

3. Setup the cluster:
```bash
./scripts/setup.sh
```

4. Deploy the system:
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
```