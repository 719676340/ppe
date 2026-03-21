# backend/management/schemas/statistics.py
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class ZoneStatisticsResponse(BaseModel):
    zone_id: int
    zone_name: str
    camera_id: int
    camera_name: str
    violation_count: int

class PeriodStatisticsResponse(BaseModel):
    period: str  # 'morning'/'afternoon'/'night'
    violation_count: int

class CameraStatisticsResponse(BaseModel):
    camera_id: int
    camera_name: str
    violation_count: int

class TrendDataPoint(BaseModel):
    date: str
    count: int

class TrendStatisticsResponse(BaseModel):
    data: List[TrendDataPoint]
