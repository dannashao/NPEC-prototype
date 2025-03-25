import os
import json
import logging
from typing import Dict, Optional, Any
import pandas as pd

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

    def validate_sensor_data(self, df: pd.DataFrame) -> bool:
        """Validate sensor data structure"""
        required_columns = {'Tmean.air', 'RHmean.air', 'Rad'}
        missing_columns = required_columns - set(df.columns)
        
        if missing_columns:
            logger.error(f"Missing required columns in sensor data: {missing_columns}")
            logger.error(f"Available columns: {df.columns.tolist()}")
            return False
        return True

    def prepare_sensor_row(self, row: pd.Series) -> Dict[str, Any]:
        """Prepare sensor data row for transmission"""
        return {
            'timestamp': pd.Timestamp.now().isoformat(),
            'temperature': float(row['Tmean.air']),
            'humidity': float(row['RHmean.air']),
            'light': float(row['Rad'])
        }

    def prepare_form_data(self, sensor_row: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare form data for transmission"""
        if not self.gene_variety:
            raise ValueError("Plant configuration not loaded")
            
        return {
            'plant_name': self.plant_name,
            'gene_variety': self.gene_variety,
            'sensor_data': json.dumps(sensor_row)
        } 