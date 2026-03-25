# backend/management/schemas/violation.py
from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime, timezone

class ViolationBase(BaseModel):
    camera_id: int
    zone_id: Optional[int] = None
    violation_time: datetime
    image_path: Optional[str] = None
    is_processed: bool = False
    remark: Optional[str] = None

class ViolationResponse(BaseModel):
    id: int
    camera_id: int
    zone_id: Optional[int] = None
    violation_time: datetime
    image_path: Optional[str] = None
    is_processed: bool = False
    remark: Optional[str] = None
    created_at: datetime
    camera_name: Optional[str] = None
    zone_name: Optional[str] = None

    @field_serializer('violation_time')
    def serialize_violation_time(self, value: datetime | None) -> str:
        """将UTC时间转换为本地时间字符串"""
        if value is None:
            return ""
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        local_time = value.astimezone()
        return local_time.strftime('%Y-%m-%d %H:%M:%S')

    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime | None) -> str:
        """将UTC时间转换为本地时间字符串"""
        if value is None:
            return ""
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        local_time = value.astimezone()
        return local_time.strftime('%Y-%m-%d %H:%M:%S')

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
