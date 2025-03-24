# Plant Monitoring System

A Kubernetes-based system for monitoring plant sensor data and images, with genomic data integration.

## System Architecture

The system consists of the following components:
- **Plant Sender**: Sends sensor data and plant images
- **Receiver**: REST API service that processes incoming data
- **MongoDB**: Database for storing sensor data, images, and genomic information

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

2. Setup the cluster:
```bash
./scripts/setup.sh
```

3. Deploy the system:
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
- Images (optional)
- Genomic Data (linked via Gene Variety)

## Configuration

### Environment Variables

Plant Sender:
- `PLANT_NAME`: Name of the plant (default: "plant1")
- `GENE_VARIETY`: Genetic variety ID (default: "11430")
- `RECEIVER_URL`: URL of the receiver service

Receiver:
- `MONGODB_URI`: MongoDB connection string
- `GENOMIC_DATA_PATH`: Path to genomic data file

## API Endpoints

- `POST /receive_data`: Receives plant data and images
- `GET /health`: Health check endpoint

## Monitoring

Common monitoring commands:
```bash
# View system status
kubectl get pods

# Check component logs
kubectl logs -l app=plant-sender
kubectl logs -l app=receiver

# View services
kubectl get services
```

## Troubleshooting

If you encounter issues:
1. Check pod status: `kubectl get pods`
2. View application logs: `kubectl logs -l app=<component-name>`
3. Ensure all prerequisites are installed
4. Verify network connectivity: `kubectl get ingress`

## Cleanup

Remove all resources:
```bash
kind delete cluster --name plant-cluster
```
```

Key changes made:
1. Removed project structure section (as it's self-explanatory from the repository)
2. Consolidated data structure sections into "Data Model"
3. Removed duplicate monitoring and configuration sections
4. Simplified the API endpoints section
5. Removed redundant setup and deployment instructions that are in the scripts
6. Made troubleshooting more concise with direct commands
7. Removed features section as they're covered in the architecture
8. Removed data flow section as it's implementation detail