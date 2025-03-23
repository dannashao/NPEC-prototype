# Plant Data Flow Simulation

This project simulates a data flow system where plant data (images and sensor readings) are periodically sent from multiple plant sources to a central receiver that stores the data in MongoDB.

## Project Structure

```
.
├── data/                    # Data directory
│   ├── plant1/             # Plant 1 data
│   │   ├── images/         # Plant 1 images
│   │   └── sensor_data.csv # Plant 1 sensor data
│   ├── plant2/             # Plant 2 data
│   │   ├── images/         # Plant 2 images
│   │   └── sensor_data.csv # Plant 2 sensor data
│   └── genomic_data.json    # Genomic data for plants
├── docker/                 # Docker configurations
│   ├── plant-sender/       # Plant data sender service (sender.py)
│   └── receiver/          # Data receiver service
├── deployments/           # Kubernetes deployment files
└── scripts/              # Utility scripts
```

## Prerequisites

- Docker
- Kind (Kubernetes in Docker)
- kubectl
- Tailscale (for external access)

## Setup

1. Start Kind cluster and enable Ingress:
   ```bash
   chmod +x scripts/start.sh
   ./scripts/start.sh
   ```
   This will:
   - Create a Kind cluster using the provided `kind-config.yaml`
   - Configure port mappings (80/443) for external access
   - Enable the Ingress controller
   - Set up required host entries

2. Build Docker images:
   ```bash
   # Build plant sender
   docker build -t plant-sender:latest docker/plant-sender/
   
   # Build receiver
   docker build -t plant-receiver:latest docker/receiver/
   ```

3. Load images into Kind cluster:
   ```bash
   kind load docker-image plant-sender:latest --name plant-cluster
   kind load docker-image plant-receiver:latest --name plant-cluster
   ```

4. Deploy the application:
   ```bash
   kubectl apply -f deployments/
   ```

## Usage

### Scaling Plant Senders

To add more plant senders, you can scale the deployment:
```bash
kubectl scale deployment plant-sender --replicas=2
```

### Accessing the Application

1. MongoDB Web Interface (Mongo Express):
   - URL: http://plant-data.local/mongo-express
   - Access MongoDB data through the web interface

2. Receiver API:
   - Base URL: http://plant-data.local/receiver
   - Endpoint: POST /receive

### Monitoring

- Check pod status:
  ```bash
  kubectl get pods
  ```
- View logs:
  ```bash
  kubectl logs -f deployment/plant-sender
  kubectl logs -f deployment/receiver
  ```

## Features

- Scalable plant data senders
- Automatic error injection (10% chance)
- MongoDB storage with persistent volume
- Genomic data linking
- Web interface for data visualization
- External access via Kind Ingress and Tailscale

## Data Flow

1. Plant senders periodically send (in queue):
   - One image from the plant's image directory
   - One row from the plant's sensor data CSV
   - 10% chance of sending blank data to simulate errors

2. Receiver service:
   - Captures incoming data
   - Stores images in MongoDB GridFS
   - Stores sensor data in MongoDB collections
   - Links data with genomic information
   - Logs any errors in data reception or processing

## Cleanup

To clean up the deployment:
```bash
kubectl delete -f deployments/
kind delete cluster --name plant-cluster
```