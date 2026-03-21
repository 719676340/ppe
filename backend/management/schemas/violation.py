# backend/management/schemas/violation.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ViolationBase(BaseModel):
    camera_id: int
    zone_id: Optional[int] = None
    violation_time: datetime
    image_path: Optional[str] = None
    is_processed: bool = False
    remark: Optional[str] = None

class ViolationResponse(ViolationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ViolationListResponse(BaseModel):
    total: int
    items: list[ViolationResponse]

class ViolationFilter(BaseModel):
    camera_id: Optional[int] = None
    zone_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_processed: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
