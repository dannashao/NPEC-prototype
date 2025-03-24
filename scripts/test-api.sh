#!/bin/bash
set -e

# Function to test endpoint with retry
test_endpoint() {
    local url=$1
    local max_attempts=5
    local attempt=1
    
    echo "Testing endpoint: $url"
    while [ $attempt -le $max_attempts ]; do
        echo "Attempt $attempt of $max_attempts..."
        response=$(curl -s -w "\n%{http_code}" "$url")
        status_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | sed '$d')
        
        if [ "$status_code" -eq 200 ]; then
            echo "Success! Response:"
            echo "$body"
            return 0
        else
            echo "Received status code: $status_code"
            echo "Response body:"
            echo "$body"
            sleep 5
        fi
        attempt=$((attempt + 1))
    done
    echo "Failed after $max_attempts attempts"
    return 1
}

echo "Testing API connectivity..."
test_endpoint "http://plant-data.local/health"

echo -e "\nSending test data without image..."
curl -v -X POST http://plant-data.local/receive_data \
  -F "plant_name=plant1" \
  -F "gene_variety=11430" \
  -F 'sensor_data={"timestamp": "2024-03-24 10:00:00", "temperature": 23.5, "humidity": 65.0, "light": 800.0}'

echo -e "\nCreating test image..."
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=" | base64 -d > test.png

echo -e "\nSending test data with image..."
curl -v -X POST http://plant-data.local/receive_data \
  -F "plant_name=plant1" \
  -F "gene_variety=11430" \
  -F 'sensor_data={"timestamp": "2024-03-24 10:05:00", "temperature": 23.8, "humidity": 66.0, "light": 820.0}' \
  -F "image=@test.png"

# Clean up
rm test.png

echo -e "\nVerifying data in MongoDB..."
POD_NAME=$(kubectl get pod -l app=mongodb -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD_NAME -- mongosh --eval 'use plant_data; db.plant_data.find().sort({timestamp:-1}).limit(2).pretty()'

echo -e "\nTest complete!" 