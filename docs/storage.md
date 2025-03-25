# Storage Configuration

## Storage Types

The system uses two types of persistent storage:

1. MongoDB Storage (`mongodb-storage.yml`):
   - Stores the MongoDB database
   - 1GB capacity
   - ReadWriteOnce access mode

2. ConfigMap Storage:
   - Genomic data
   - Plant configurations
   - Sensor data templates

Note: Plant data and images are mounted directly from the host using hostPath volumes in the StatefulSet configuration.

## ConfigMaps

### Genomic Data ConfigMap
The system uses a ConfigMap to store genomic data for different plant varieties:

1. Create the ConfigMap from JSON file:
```bash
kubectl create configmap genomic-data --from-file=genomic_data=data/genomic_data.json
```

2. Verify the ConfigMap contents:
```bash
# View all variety IDs
kubectl get configmap genomic-data -o jsonpath='{.data.genomic_data}' | jq '.[].VarietyID'

# Expected output:
"11430"
"A3"
"A310"
```

3. View full genomic data:
```bash
kubectl get configmap genomic-data -o jsonpath='{.data.genomic_data}' | jq '.'
```
