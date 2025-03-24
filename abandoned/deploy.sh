#!/bin/bash
set -e

echo "🌱 Deploying Plant Monitoring System..."

# Create Kind cluster if it doesn't exist
if ! kind get clusters | grep -q "^plant-cluster$"; then
    echo "Creating Kubernetes cluster..."
    kind create cluster --name plant-cluster
    
    # Install Ingress controller
    echo "Installing Ingress controller..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
    
    # Wait for Ingress controller
    echo "Waiting for Ingress controller..."
    kubectl wait --namespace ingress-nginx \
      --for=condition=ready pod \
      --selector=app.kubernetes.io/component=controller \
      --timeout=300s
fi

# Clean up existing resources
echo "Cleaning up existing resources..."
kubectl delete deployment,service,configmap,pvc --all --ignore-not-found=true
sleep 5

# Build and load Docker images
echo "Building Docker images..."
docker build -t receiver:latest docker/receiver/
docker build -t sender:latest docker/plant-sender/

echo "Loading images into cluster..."
kind load docker-image receiver:latest --name plant-cluster
kind load docker-image sender:latest --name plant-cluster

# Apply Kubernetes configurations
echo "Applying configurations..."

# Create ConfigMaps
kubectl apply -f deployments/mongodb-init-configmap.yml
kubectl apply -f deployments/genomic-data-configmap.yml

# Deploy MongoDB
kubectl apply -f deployments/mongodb-deployment.yml
echo "Waiting for MongoDB..."
kubectl wait --for=condition=ready pod -l app=mongodb --timeout=120s

# Deploy receiver
kubectl apply -f deployments/receiver-deployment.yml
echo "Waiting for receiver..."
kubectl wait --for=condition=ready pod -l app=receiver --timeout=120s

# Deploy sender
kubectl apply -f deployments/sender-deployment.yml
echo "Waiting for sender..."
kubectl wait --for=condition=ready pod -l app=plant-sender --timeout=120s

# Configure ingress
kubectl apply -f deployments/ingress.yml

# Add host entry
CLUSTER_IP=$(docker container inspect plant-cluster-control-plane --format '{{ .NetworkSettings.Networks.kind.IPAddress }}')
if [ -z "$CLUSTER_IP" ]; then
    echo "Error: Could not get cluster IP"
    exit 1
fi
echo "Adding host entry..."
echo "$CLUSTER_IP plant-data.local" | sudo tee -a /etc/hosts

echo "✅ Deployment complete!"
echo "
System is accessible at:
  - API: http://plant-data.local/

To monitor the system:
  - Check pod status: kubectl get pods
  - View sender logs: kubectl logs -l app=plant-sender
  - View receiver logs: kubectl logs -l app=receiver
"

# Show system status
echo "Current system status:"
kubectl get pods,svc,ingress 