#!/bin/bash

# Exit on error
set -e

# Function to show usage
show_usage() {
    echo "Usage: $0 [--clean]"
    echo "Options:"
    echo "  --clean    Perform a complete cleanup of all resources before setup"
    exit 1
}

# Function to perform cleanup
cleanup() {
    echo "Performing complete cleanup..."
    
    # Delete deployments and services
    kubectl delete deployment miappe-checker --ignore-not-found
    kubectl delete service miappe-checker --ignore-not-found
    kubectl delete statefulset miappe-postgres --ignore-not-found
    kubectl delete service miappe-postgres --ignore-not-found
    
    # Delete configmaps
    kubectl delete configmap miappe-postgres-config --ignore-not-found
    kubectl delete configmap miappe-postgres-init --ignore-not-found
    
    # Delete PVCs
    kubectl delete pvc postgres-data-miappe-postgres-0 --ignore-not-found
    kubectl delete pvc miappe-postgres-pvc --ignore-not-found
    
    # Delete PVs (get all PVs related to our app and delete them)
    for pv in $(kubectl get pv | grep "postgres-data-miappe-postgres" | awk '{print $1}'); do
        kubectl delete pv $pv --ignore-not-found
    done
    
    # Wait for resources to be deleted
    echo "Waiting for resources to be deleted..."
    sleep 10
    
    # Verify cleanup
    echo "Verifying cleanup..."
    if kubectl get pvc | grep -q "postgres-data-miappe-postgres"; then
        echo "Warning: Some PVCs still exist. You may need to delete them manually."
    fi
    if kubectl get pv | grep -q "postgres-data-miappe-postgres"; then
        echo "Warning: Some PVs still exist. You may need to delete them manually."
    fi
}

# Parse command line arguments
CLEAN=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN=true
            shift
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            ;;
    esac
done

echo "Setting up MIAPPE Checker..."

# Check if we're in the correct directory
if [ ! -f "setup_miappe.sh" ]; then
    echo "Please run this script from the miappe_checker/scripts directory"
    exit 1
fi

# Check if Kind cluster exists
if ! kind get clusters | grep -q "plant-cluster"; then
    echo "Error: Kind cluster 'plant-cluster' not found"
    exit 1
fi

# Perform cleanup if requested
if [ "$CLEAN" = true ]; then
    cleanup
fi

# Apply PostgreSQL configuration
echo "Applying PostgreSQL configuration..."
kubectl apply -f ../deployments/miappe-postgres-config.yml
kubectl apply -f ../deployments/miappe-postgres-init.yml

# Apply PostgreSQL StatefulSet
echo "Applying PostgreSQL StatefulSet..."
kubectl apply -f ../deployments/miappe-postgres.yml

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=miappe-postgres --timeout=120s

# Build and load Docker images
echo "Building Docker images..."
cd ..
docker build -t miappe-checker-web:latest -f docker/web/Dockerfile .
docker build -t miappe-checker-backend:latest -f docker/backend/Dockerfile .
cd scripts

# Load images into kind cluster
echo "Loading images into kind cluster..."
kind load docker-image miappe-checker-web:latest --name plant-cluster
kind load docker-image miappe-checker-backend:latest --name plant-cluster

# Apply MIAPPE Checker deployment
echo "Applying MIAPPE Checker deployment..."
kubectl apply -f ../deployments/miappe-checker-deployment.yml

# Wait for deployment to be ready
echo "Waiting for MIAPPE Checker to be ready..."
kubectl wait --for=condition=available deployment/miappe-checker --timeout=120s

echo "MIAPPE Checker setup complete!" 