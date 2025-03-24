#!/bin/bash
set -e

# Verify cluster exists and is ready
if ! kind get clusters | grep -q "^plant-cluster$"; then
    echo "Error: Cluster 'plant-cluster' not found. Please run setup.sh first."
    exit 1
fi

# Verify cluster is operational
if ! kubectl cluster-info; then
    echo "Error: Cluster is not operational. Please run setup.sh first."
    exit 1
fi

# Function to check if a command succeeded
check_status() {
    if [ $? -ne 0 ]; then
        echo "Error: $1"
        exit 1
    fi
}

# Function to wait for pod readiness
wait_for_pod() {
    local label=$1
    local timeout=$2
    echo "Waiting for pod with label $label to be ready..."
    kubectl wait --for=condition=Ready pod -l app=$label --timeout=${timeout}s
    check_status "Pod $label failed to become ready within ${timeout}s"
}

echo "Starting deployment process..."

# 1. Clean up all existing resources
echo "Cleaning up existing resources..."
kubectl delete ingress,deployment,service,configmap,pv,pvc --all --ignore-not-found=true

# Wait for resources to be deleted
echo "Waiting for resources to be cleaned up..."
sleep 5

# 2. Rebuild and reload Docker images
echo "Building and loading Docker images..."
docker build -t plant-sender:latest docker/plant-sender/
check_status "Failed to build plant-sender image"

docker build -t receiver:latest docker/receiver/
check_status "Failed to build receiver image"

kind load docker-image plant-sender:latest --name plant-cluster
check_status "Failed to load plant-sender image into kind cluster"

kind load docker-image receiver:latest --name plant-cluster
check_status "Failed to load receiver image into kind cluster"

# 3. Create storage resources
echo "Creating storage resources..."
# Ensure the host paths exist
docker exec plant-cluster-control-plane mkdir -p /tmp/data/images /tmp/data/mongodb
check_status "Failed to create host directories"

# Create MongoDB PV/PVC
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mongodb-pv
spec:
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: standard
  hostPath:
    path: /tmp/data/mongodb
    type: DirectoryOrCreate
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongodb-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 1Gi
EOF
check_status "Failed to create MongoDB storage resources"

# Create image storage PV/PVC
kubectl apply -f deployments/image-storage.yml
check_status "Failed to create image storage resources"

# 4. Apply ConfigMaps
echo "Applying ConfigMaps..."
kubectl apply -f deployments/mongodb-init-configmap.yml
check_status "Failed to apply MongoDB init ConfigMap"

kubectl apply -f deployments/genomic-data-configmap.yml
check_status "Failed to apply genomic data ConfigMap"

# Create plant-data ConfigMap
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: plant-data
data:
  "plant1.sensor_data.csv": |
    timestamp,temperature,humidity,light
    2024-03-23 00:00:00,22.5,65.0,800.0
    2024-03-23 00:10:00,22.8,64.0,820.0
    2024-03-23 00:20:00,22.3,66.0,780.0
EOF
check_status "Failed to create plant-data ConfigMap"

# 5. Deploy MongoDB
echo "Deploying MongoDB..."
kubectl apply -f deployments/mongodb-deployment.yml
check_status "Failed to apply MongoDB deployment"

# Wait for MongoDB PVC to bind
echo "Waiting for MongoDB PVC to bind..."
for i in {1..30}; do
    if kubectl get pvc mongodb-pvc | grep -q Bound; then
        echo "MongoDB PVC successfully bound"
        break
    fi
    echo "Waiting for MongoDB PVC to bind... attempt $i/30"
    sleep 2
done

# Now wait for MongoDB pod
wait_for_pod "mongodb" 120

# Give MongoDB time to initialize
echo "Waiting for MongoDB to initialize..."
sleep 20

# Deploy MongoDB Express
echo "Deploying MongoDB Express..."
kubectl apply -f deployments/mongo-express-deployment.yml
check_status "Failed to apply MongoDB Express deployment"
wait_for_pod "mongo-express" 60

# 6. Deploy receiver
echo "Deploying receiver..."
kubectl apply -f deployments/receiver-deployment.yml
check_status "Failed to apply receiver deployment"
wait_for_pod "receiver" 60

# 7. Deploy sender (which will trigger PVC binding)
echo "Deploying sender..."
kubectl apply -f deployments/sender-deployment.yml
check_status "Failed to apply sender deployment"

# Now wait for PVC to bind after sender deployment
echo "Waiting for PVC to be bound..."
for i in {1..30}; do
    if kubectl get pvc image-storage-pvc | grep -q Bound; then
        echo "PVC successfully bound"
        break
    fi
    echo "Waiting for PVC to bind... attempt $i/30"
    sleep 2
done

# Wait for sender pod to be ready
wait_for_pod "plant-sender" 60

# Apply ingress configuration
echo "Applying ingress configuration..."
kubectl apply -f deployments/ingress.yml
check_status "Failed to apply ingress configuration"

# 9. Verify all resources
echo -e "\nVerifying resources..."
echo -e "\nPersistent Volumes and Claims:"
kubectl get pv,pvc

echo -e "\nConfigMaps:"
kubectl get configmaps

echo -e "\nPods:"
kubectl get pods

echo -e "\nServices:"
kubectl get svc

echo -e "\nIngress:"
kubectl get ingress

echo -e "\nDeployment completed successfully!"
echo "You can access the application at:"
echo "- API: http://plant-data.local/"

# Monitor pod status
echo -e "\nMonitoring pod status..."
kubectl get pods -w