from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Dict, Optional
import os
from datetime import datetime

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://miappe_user:miappe_password@db:5432/miappe")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MIAPPEData(BaseModel):
    INVESTIGATION: Optional[Dict] = None
    STUDY: Optional[Dict] = None
    PERSON: Optional[Dict] = None
    DATA_FILE: Optional[Dict] = None
    BIOLOGICAL_MATERIAL: Optional[Dict] = None
    ENVIRONMENT: Optional[Dict] = None
    EXPERIMENTAL_FACTOR: Optional[Dict] = None
    EVENT: Optional[Dict] = None
    OBSERVATION_UNIT: Optional[Dict] = None
    SAMPLE: Optional[Dict] = None
    OBSERVED_VARIABLE: Optional[Dict] = None
    status: str

@app.post("/miappe/save_checklist")
async def save_checklist(data: MIAPPEData):
    db = SessionLocal()
    try:
        # Start transaction
        if data.INVESTIGATION:
            # Insert investigation data
            investigation_data = data.INVESTIGATION
            # Add your SQL insert statements here
            
        if data.STUDY:
            # Insert study data
            study_data = data.STUDY
            # Add your SQL insert statements here
            
        # Continue with other scopes...
        
        db.commit()
        return {"success": True, "message": "Checklist saved successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 