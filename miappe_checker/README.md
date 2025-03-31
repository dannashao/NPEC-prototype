# MIAPPE Metadata Checker

A web-based tool for validating and managing MIAPPE (Minimum Information About a Plant Phenotyping Experiment) metadata. This component is part of the NPEC Prototype system and provides a user-friendly interface for managing plant experiment metadata.

## Features

- **Interactive Form Interface**: Two-stage form for entering investigation and study IDs, followed by detailed metadata entry
- **Real-time Validation**: Immediate feedback on mandatory fields and data format requirements
- **MongoDB Field Binding**: Visual interface for mapping MongoDB fields to MIAPPE metadata fields
- **Persistent Storage**: PostgreSQL database for storing validated MIAPPE metadata
- **Field Requirement Levels**: Clear indication of mandatory, recommended, and optional fields
- **Responsive Design**: Works well on both desktop and mobile devices

## Components

### Frontend
- HTML/CSS/JavaScript-based web interface
- Dynamic form generation based on MIAPPE schema
- Real-time field validation and binding management
- Responsive design with modern UI/UX

### Backend
- Flask-based REST API
- PostgreSQL database for metadata storage
- MongoDB integration for field binding
- MIAPPE schema validation

## Setup and Deployment

The MIAPPE Checker can be easily deployed using the provided automation script:

```bash
cd miappe_checker/scripts
./setup_miappe.sh [--clean]
```

The script performs the following actions:
1. Verifies the Kind cluster exists
2. Optionally cleans up existing resources (with `--clean` flag)
3. Applies PostgreSQL configurations and initializes the database
4. Builds and loads Docker images for web and backend components
5. Deploys the MIAPPE Checker application

### Prerequisites
- Running Kind cluster named 'plant-cluster'
- kubectl configured to access the cluster
- Docker installed and running

### Options
- `--clean`: Performs a complete cleanup of existing resources before setup
- `--help`: Shows usage information

### Cleanup
The `--clean` option removes:
- Deployments and services
- ConfigMaps
- Persistent Volume Claims (PVCs)
- Persistent Volumes (PVs)

## API Endpoints

- `GET /miappe/`: Main application interface
- `POST /miappe/api/check_investigation`: Check/create investigation and study records
- `POST /miappe/api/save_checklist`: Save MIAPPE metadata

## Database Schema

The system uses two databases:
1. **PostgreSQL**: Stores MIAPPE metadata with proper schema validation
2. **MongoDB**: Stores plant data fields that can be bound to MIAPPE fields

## Usage

1. Enter Investigation and Study IDs
2. Fill in required metadata fields
3. Bind MongoDB fields to MIAPPE fields using the dropdown interface
4. Save the checklist

## Integration with NPEC Prototype

This component is designed to work seamlessly with the NPEC Prototype system:
- Receives plant data from MongoDB
- Validates metadata against MIAPPE standards
- Stores validated metadata in PostgreSQL
- Provides a user interface for metadata management

## Troubleshooting

If you encounter issues during setup:
1. Ensure the Kind cluster is running: `kind get clusters`
2. Check pod status: `kubectl get pods`
3. View logs: `kubectl logs -l app=miappe-checker`
4. Verify PostgreSQL is running: `kubectl get pods -l app=miappe-postgres`
5. Check for persistent volume issues: `kubectl get pv,pvc`
