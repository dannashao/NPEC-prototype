import os
import json
import logging
from typing import Dict, Optional, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class PlantDataProcessor:
    def __init__(self, plant_name: str, config_path: str):
        self.plant_name = plant_name
        self.config_path = config_path
        self.gene_variety = None
        self.plant_config = None

    def load_plant_config(self) -> Dict[str, Any]:
        """Load plant configuration from config file"""
        try:
            with open(self.config_path, "r") as f:
                configs = json.load(f)
            
            if self.plant_name not in configs:
                raise ValueError(f"No configuration found for {self.plant_name}")
                
            self.plant_config = configs[self.plant_name]
            self.gene_variety = self.plant_config["gene_variety"]
            return self.plant_config
        except Exception as e:
            logger.error(f"Error loading plant configuration: {e}")
            raise

    def validate_sensor_data(self, df: pd.DataFrame) -> tuple[bool, set]:
        """Validate sensor data CSV structure
        
        Returns:
            tuple: (is_valid, missing_columns)
        """
        required_columns = {'Tmean.air', 'RHmean.air', 'Rad'}
        
        if df.empty:
            logger.warning("Empty sensor data DataFrame")
            return False, required_columns
        
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            logger.warning(f"Missing columns in sensor data: {missing_columns}")
        
        return (len(missing_columns) == 0, missing_columns)

    def prepare_sensor_row(self, row: pd.Series) -> Dict[str, Any]:
        """Prepare sensor data row for transmission"""
        try:
            return {
                'timestamp': pd.Timestamp.now().isoformat(),
                'temperature': float(row.get('Tmean.air', float('nan'))),
                'humidity': float(row.get('RHmean.air', float('nan'))),
                'light': float(row.get('Rad', float('nan')))
            }
        except (ValueError, TypeError) as e:
            logger.warning(f"Error preparing sensor row: {e}")
            return {
                'timestamp': pd.Timestamp.now().isoformat(),
                'temperature': float('nan'),
                'humidity': float('nan'),
                'light': float('nan')
            }

    def prepare_form_data(self, sensor_row: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare form data for transmission"""
        if not self.gene_variety:
            raise ValueError("Plant configuration not loaded")
            
        # Custom JSON encoder for NaN values
        class NaNEncoder(json.JSONEncoder):
            def default(self, obj):
                # Handle numpy float types
                if isinstance(obj, float) or isinstance(obj, np.float64):
                    if np.isnan(obj):
                        return None
                    return float(obj)
                if pd.isna(obj):
                    return None
                return super().default(obj)
        
        # Convert NaN values to None before serialization
        processed_row = {}
        for key, value in sensor_row.items():
            if pd.isna(value):
                processed_row[key] = None
            else:
                processed_row[key] = value
        
        return {
            'plant_name': self.plant_name,
            'gene_variety': self.gene_variety,
            'sensor_data': json.dumps(processed_row, cls=NaNEncoder)
        } 