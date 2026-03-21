# backend/management/schemas/zone.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DetectionZoneBase(BaseModel):
    camera_id: int
    name: str = Field(..., min_length=1, max_length=100)
    coordinates: str  # JSON格式: [[x1,y1],[x2,y2],...]
    enabled: bool = True

class DetectionZoneCreate(DetectionZoneBase):
    pass

class DetectionZoneUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    coordinates: Optional[str] = None
    enabled: Optional[bool] = None

class DetectionZoneResponse(DetectionZoneBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
