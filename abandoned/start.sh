#!/bin/bash


# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


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
echo "This might take a few minutes..."
for i in {1..5}; do
    if kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s; then
        break
    fi
    echo "Attempt $i failed, retrying..."
    if [ $i -eq 5 ]; then
        echo "Warning: Ingress controller didn't become ready in time, but continuing..."
    fi
    sleep 10
done

# Get cluster IP
CLUSTER_IP=$(docker container inspect plant-cluster-control-plane --format '{{ .NetworkSettings.Networks.kind.IPAddress }}')
if [ -z "$CLUSTER_IP" ]; then
    echo "Error: Could not get cluster IP"
    exit 1
fi
echo "Cluster IP: $CLUSTER_IP"

# Add host entries (requires sudo)
echo "Adding host entries..."
echo "$CLUSTER_IP plant-data.local" | sudo tee -a /etc/hosts


echo "Kind cluster is ready with Ingress enabled!"
echo "You can now deploy your applications using kubectl apply -f deployments/"