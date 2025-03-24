#!/bin/bash
set -e

echo "🗑️ Cleaning up existing Kind resources..."

# Stop and remove all Docker containers related to Kind
echo "Stopping and removing Kind-related containers..."
docker ps -a | grep 'kind-' | awk '{print $1}' | xargs -r docker rm -f
docker ps -a | grep 'plant-cluster-' | awk '{print $1}' | xargs -r docker rm -f

# Delete any existing Kind cluster
echo "Deleting Kind cluster..."
kind delete clusters --all

# Remove any Kind networks
echo "Cleaning up Docker networks..."
docker network prune -f

# Give system time to cleanup
echo "Waiting for cleanup..."
sleep 10

echo "🚀 Creating new Kind cluster with port mappings..."
kind create cluster --name plant-cluster --config scripts/kind-config.yaml

# Verify cluster creation
echo "Verifying cluster creation..."
if ! kind get clusters | grep -q "^plant-cluster$"; then
    echo "Error: Failed to create cluster"
    exit 1
fi

# Wait for the cluster to be ready
echo "Waiting for cluster nodes to be ready..."
kubectl wait --for=condition=ready node --all --timeout=60s

echo "📦 Installing ingress-nginx..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

echo "⏳ Waiting for ingress-nginx namespace..."
kubectl wait --timeout=90s --for=condition=Ready -n ingress-nginx pod --all || true

# Wait for the ingress controller pod to be created
echo "Waiting for ingress controller pod to be created..."
while ! kubectl get pods -n ingress-nginx -l app.kubernetes.io/component=controller 2>/dev/null; do
    echo "Waiting for ingress controller pod..."
    sleep 5
done

echo "⏳ Waiting for ingress-nginx to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s || true

# Verify cluster is operational
echo "Verifying cluster is operational..."
if ! kubectl cluster-info; then
    echo "Error: Cluster is not operational"
    exit 1
fi

# Get cluster IP
CONTAINER_NAME="plant-cluster-control-plane"
CLUSTER_IP=$(docker container inspect "$CONTAINER_NAME" --format '{{ .NetworkSettings.Networks.kind.IPAddress }}')

if [ -z "$CLUSTER_IP" ]; then
    echo "Error: Could not get cluster IP"
    echo "Available containers:"
    docker ps
    exit 1
fi

echo "Adding host entry..."
if ! grep -q "plant-data.local" /etc/hosts; then
    echo "$CLUSTER_IP plant-data.local" | sudo tee -a /etc/hosts
else
    # Update existing entry
    sudo sed -i "s/.*plant-data.local/$CLUSTER_IP plant-data.local/" /etc/hosts
fi

echo "✅ Setup complete!"
echo "Cluster is ready and accessible at: $CLUSTER_IP" 