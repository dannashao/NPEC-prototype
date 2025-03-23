#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check and stop services using port 80/443
echo "Checking for services using ports 80/443..."
if [ "$(lsof -i:80 -t)" ]; then
    echo "Port 80 is in use. Please stop the service using it first."
    echo "You can try: sudo lsof -i:80 to see which service it is"
    exit 1
fi


# Create Kind cluster if it doesn't exist
if ! kind get clusters | grep -q "plant-cluster"; then
    echo "Creating Kind cluster 'plant-cluster'..."
    kind create cluster --name plant-cluster --config "${SCRIPT_DIR}/kind-config.yaml"
fi

# Wait for the cluster to be ready
echo "Waiting for cluster to be ready..."
kubectl wait --for=condition=ready node --all --timeout=120s

# Enable Ingress controller
echo "Enabling Ingress controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for Ingress controller to be ready
echo "Waiting for Ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# Get cluster IP
CLUSTER_IP=$(docker container inspect plant-cluster-control-plane --format '{{ .NetworkSettings.Networks.kind.IPAddress }}')
echo "Cluster IP: $CLUSTER_IP"

# Add host entries (requires sudo)
echo "Adding host entries..."
echo "$CLUSTER_IP plant-data.local" | sudo tee -a /etc/hosts

echo "Kind cluster is ready with Ingress enabled!"
echo "You can now deploy your applications using kubectl apply -f deployments/"