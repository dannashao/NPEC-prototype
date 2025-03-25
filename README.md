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
- Kubernetes (Kind)
- kubectl

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/dannashao/NPEC-prototype.git
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