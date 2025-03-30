from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

'''
This script:
1. Defines data classes for MIAPPE fields and scopes
2. Implements a schema manager that:
    - Loads the CSV file
    - Parses scope and field definitions
    - Provides validation methods
    - Identifies mandatory fields
3. Handles requirements levels:
    - 0: mandatory
    - 1: recommended
    - 2: if available
    - 3: read-only
4. Provides methods to:
    - Get mandatory fields for a scope
    - Validate data against scope requirements
    - Print schema summary
'''

@dataclass
class MIAPPEField:
    """Represents a MIAPPE field specification"""
    codename: str
    requirement: int  # 0: mandatory, 1: recommended, 2: if available, 3: read-only
    definition: str
    example: str
    format: str
    cardinality: str

@dataclass
class MIAPPEScope:
    """Represents a MIAPPE scope with its fields"""
    name: str
    requirement: int
    fields: Dict[str, MIAPPEField]
    description: str

class MIAPPESchema:
    """Manages the MIAPPE schema definition"""
    def __init__(self):
        self.scopes: Dict[str, MIAPPEScope] = {}
        
    def load_from_csv(self, filepath: str) -> None:
        """Load MIAPPE schema from CSV file"""
        try:
            df = pd.read_csv(filepath, sep='\t')
            current_scope = None
            
            for _, row in df.iterrows():
                # Check if this is a scope definition
                if pd.notna(row['MIAPPE Check list']) and pd.isna(row['Codename']):
                    scope_name = row['MIAPPE Check list'].strip()
                    scope_req = int(row['Requirement'])
                    scope_desc = row['Definition'] if pd.notna(row['Definition']) else ""
                    
                    current_scope = MIAPPEScope(
                        name=scope_name,
                        requirement=scope_req,
                        fields={},
                        description=scope_desc
                    )
                    self.scopes[scope_name] = current_scope
                    logger.info(f"Loaded scope: {scope_name} (requirement: {scope_req})")
                
                # Process field definition
                elif current_scope and pd.notna(row['Codename']):
                    field = MIAPPEField(
                        codename=row['Codename'],
                        requirement=int(row['Requirement']),
                        definition=row['Definition'] if pd.notna(row['Definition']) else "",
                        example=row['Example'] if pd.notna(row['Example']) else "",
                        format=row['Format'] if pd.notna(row['Format']) else "",
                        cardinality=row['Cardinality'] if pd.notna(row['Cardinality']) else ""
                    )
                    current_scope.fields[field.codename] = field
                    logger.debug(f"Added field {field.codename} to scope {current_scope.name}")
        except Exception as e:
            logger.error(f"Failed to load MIAPPE schema from {filepath}: {e}")
            raise
    
    def get_mandatory_fields(self, scope_name: str) -> List[str]:
        """Get list of mandatory fields for a scope"""
        scope = self.scopes.get(scope_name)
        if not scope:
            return []
        return [
            field.codename 
            for field in scope.fields.values() 
            if field.requirement == 0
        ]
    
    def validate_scope(self, scope_name: str, data: Dict) -> List[str]:
        """Validate data against scope requirements"""
        errors = []
        scope = self.scopes.get(scope_name)
        
        if not scope:
            return [f"Unknown scope: {scope_name}"]
            
        # Check mandatory fields
        mandatory_fields = self.get_mandatory_fields(scope_name)
        for field in mandatory_fields:
            if field not in data:
                errors.append(f"Missing mandatory field: {field}")
        
        return errors

def main():
    """Example usage of the MIAPPESchema class"""
    schema = MIAPPESchema()
    schema.load_from_csv("MIAPPE_Checklist_Data_Model_with_Requirements.csv")
    
    # Print summary of loaded schema
    for scope_name, scope in schema.scopes.items():
        print(f"\nScope: {scope_name} (Requirement: {scope.requirement})")
        print(f"Description: {scope.description}")
        print("Mandatory fields:")
        for field_name in schema.get_mandatory_fields(scope_name):
            field = scope.fields[field_name]
            print(f"  - {field_name}: {field.definition}")

if __name__ == "__main__":
    main() 