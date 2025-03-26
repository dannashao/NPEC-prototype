#!/bin/bash
set -e

echo "Setting up MIAPPE Checker..."

# Clean up existing resources
echo "Cleaning up existing resources..."
kubectl delete deployment miappe-checker --ignore-not-found=true
kubectl delete service miappe-checker-service --ignore-not-found=true
kubectl delete configmap miappe-schema-config --ignore-not-found=true

# Create ConfigMap from MIAPPE schema
kubectl create configmap miappe-schema-config \
  --from-file=../src/models/MIAPPE_Checklist_Data_Model_with_Requirements.csv

# Build Docker image from the parent directory to include src
cd ../docker/web
docker build -t localhost:5001/miappe-checker:latest -f Dockerfile ../..

# Load image into kind cluster
kind load docker-image localhost:5001/miappe-checker:latest --name plant-cluster

# Apply deployments
cd ../../deployments
kubectl apply -f miappe-checker-deployment.yml

# Update ingress by adding MIAPPE path
echo "Updating ingress configuration..."
# Get current ingress configuration
kubectl get ingress plant-data-ingress -o yaml > current-ingress.yml

# Add MIAPPE path using yq
yq e '.spec.rules[0].http.paths += [{"backend":{"service":{"name":"miappe-checker-service","port":{"number":5001}}},"path":"/miappe","pathType":"Prefix"}]' -i current-ingress.yml

# Apply updated ingress
kubectl apply -f current-ingress.yml

# Clean up temporary files
rm current-ingress.yml

echo "MIAPPE Checker setup complete!" 