# NPEC Prototype

A Kubernetes-based scalable data pipeline for multi-modal plant experimental data, incorporating real-time validation, MIAPPE metadata compliance and system monitoring.

## Quick Links
- [Data Structure Guide](docs/data-structure.md)
- [StatefulSet Configuration](docs/statefulset.md)
- [Storage Configuration](docs/storage.md)
- [Monitoring and Validation](docs/monitoring.md)
- [MIAPPE Checker Documentation](miappe_checker/README.md)

## System Architecture

The system consists of the following components:
- **Plant Sender**: Sends sensor data and plant images
- **Receiver**: REST API service that processes incoming data
- **MongoDB**: Database for storing sensor data, images, and genomic information
- **MongoDB Express**: Web-based MongoDB admin interface
- **MIAPPE Checker**: Web-based tool for validating and managing plant experiment metadata
- **PostgreSQL**: Database for storing validated MIAPPE metadata

## Prerequisites

- Docker
- Kubernetes (Kind)
- kubectl
- Python 3.8+ (for MIAPPE Checker development)

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

4. Deploy the system components:

**WARNING: These scripts delete existing resources. Use only for first-time deployment or system reset.**

```bash
# Deploy core components
./scripts/deploy.sh

# Deploy MIAPPE Checker
cd miappe_checker/scripts
./setup_miappe.sh [--clean]
```

The `setup_miappe.sh` script:
- Verifies cluster prerequisites
- Sets up PostgreSQL database
- Deploys MIAPPE Checker web interface
- Configures necessary Kubernetes resources
Use `--clean` flag for fresh installation

## Access Points

### API Endpoints
- `POST /receive_data`: Receives plant data and images
- `GET /health`: Health check endpoint
- `GET /validate`: Real-time data validation status
- `GET /validate/system`: System-wide validation status

### Web Interfaces
- **MongoDB Express**: `http://plant-data.local/mongo-express`
  - Credentials: admin/pass
- **MIAPPE Checker**: `http://plant-data.local/miappe`
  - Interface for managing plant experiment metadata

## Basic Monitoring
```bash
# View system status
kubectl get pods

# Check validation status
curl "http://plant-data.local/validate/system"

# View recent logs
kubectl logs -l app=receiver --tail=100

# View MIAPPE Checker logs
kubectl logs -l app=miappe-checker
```

See [Monitoring and Validation](docs/monitoring.md) for detailed monitoring information.

## Cleanup

Remove all resources:
```bash
# Clean up MIAPPE Checker (optional)
cd miappe_checker/scripts
./setup_miappe.sh --clean

# Remove entire cluster
kind delete cluster --name plant-cluster
```

## Troubleshooting

If you encounter issues:
1. Check pod status: `kubectl get pods`
2. View application logs: `kubectl logs -l app=<component-name>`
3. Ensure all prerequisites are installed
4. Verify network connectivity: `kubectl get ingress`
5. Check MongoDB Express access at `/mongo-express`
6. Check MIAPPE Checker access at `/miappe`
7. For MIAPPE Checker specific issues:
   - Verify PostgreSQL is running: `kubectl get pods -l app=miappe-postgres`
   - Check persistent volumes: `kubectl get pv,pvc`
   - View MIAPPE logs: `kubectl logs -l app=miappe-checker`

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

MIAPPE Checker:
- `FLASK_APP`: Application entry point (default: "app.py")
- `FLASK_ENV`: Environment mode (development/production)
- `POSTGRES_URI`: PostgreSQL connection string
- `MONGODB_URI`: MongoDB connection string 