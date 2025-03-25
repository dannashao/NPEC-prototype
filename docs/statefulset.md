# StatefulSet Configuration

The plant sender uses a StatefulSet to manage multiple plant monitoring instances:

### Pod Naming Convention
- Pods are named sequentially: `plant-sender-0`, `plant-sender-1`, etc.
- Each pod automatically maps to a corresponding plant: 
  - `plant-sender-0` → `plant1`
  - `plant-sender-1` → `plant2`

### Scaling Plants
```bash
# View current plant sender pods
kubectl get pods -l app=plant-sender

# Scale to monitor more plants
kubectl scale statefulset plant-sender --replicas=3

# Scale down if needed
kubectl scale statefulset plant-sender --replicas=1
```

### Volume Mounts
The StatefulSet configuration includes:
- Plant data volume: `/app/data`
- Configuration volume: `/app/config`

### Environment Variables
Each pod automatically gets:
- `PLANT_NAME`: Set from pod name (e.g., "plant-sender-0")
- `RECEIVER_URL`: Points to receiver service

### Monitoring StatefulSet
```bash
# Check StatefulSet status
kubectl get statefulset plant-sender

# View individual pod logs
kubectl logs plant-sender-0
kubectl logs plant-sender-1

# Check pod details
kubectl describe pod plant-sender-0
```

### Troubleshooting StatefulSet
1. Ensure data directories exist for each plant
2. Verify ConfigMaps are properly mounted
3. Check individual pod logs for specific plant issues
4. Verify pod naming matches plant data structure