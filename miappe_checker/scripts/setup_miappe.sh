#!/bin/bash
set -e

echo "Setting up MIAPPE Checker..."

# Clean up existing resources
echo "Cleaning up existing resources..."
kubectl delete deployment miappe-checker --ignore-not-found=true
kubectl delete service miappe-checker-service --ignore-not-found=true
kubectl delete configmap miappe-schema-config --ignore-not-found=true
kubectl delete statefulset miappe-postgres --ignore-not-found=true
kubectl delete service miappe-postgres --ignore-not-found=true
kubectl delete pvc miappe-postgres-pvc --ignore-not-found=true
kubectl delete configmap miappe-postgres-config --ignore-not-found=true
kubectl delete configmap miappe-postgres-init --ignore-not-found=true

# Create ConfigMaps
echo "Creating ConfigMaps..."
kubectl create configmap miappe-schema-config \
  --from-file=../src/models/MIAPPE_Checklist_Data_Model_with_Requirements.csv

# Build Docker images
echo "Building Docker images..."
cd ../docker/web
docker build -t localhost:5001/miappe-checker-web:latest -f Dockerfile ../..

cd ../backend
docker build -t localhost:5001/miappe-checker-backend:latest -f Dockerfile .

# Load images into kind cluster
echo "Loading images into kind cluster..."
kind load docker-image localhost:5001/miappe-checker-web:latest --name plant-cluster
kind load docker-image localhost:5001/miappe-checker-backend:latest --name plant-cluster

# Apply deployments
echo "Applying Kubernetes resources..."
cd ../../deployments
kubectl apply -f miappe-postgres.yml
kubectl apply -f miappe-postgres-init.yml
kubectl apply -f miappe-checker-deployment.yml

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=miappe-postgres --timeout=120s

# Update ingress by adding MIAPPE path
echo "Updating ingress configuration..."
# Get current ingress configuration
kubectl get ingress plant-data-ingress -o yaml > current-ingress.yml

# Remove all existing MIAPPE paths and add the correct one
yq e 'del(.spec.rules[0].http.paths[] | select(.backend.service.name == "miappe-checker-service"))' -i current-ingress.yml
yq e '.spec.rules[0].http.paths += [{"backend":{"service":{"name":"miappe-checker-service","port":{"number":80}}},"path":"/miappe","pathType":"Prefix"}]' -i current-ingress.yml

# Apply updated ingress
kubectl apply -f current-ingress.yml

# Clean up temporary files
rm current-ingress.yml

echo "MIAPPE Checker setup complete!" 