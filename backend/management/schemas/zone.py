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

class DetectionZoneResponse(BaseModel):
    id: int
    camera_id: int
    camera_name: Optional[str] = None  # 摄像头名称
    name: str
    coordinates: str
    enabled: bool
    created_at: datetime
