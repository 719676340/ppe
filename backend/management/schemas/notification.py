# backend/management/schemas/notification.py
from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime, timezone

class NotificationBase(BaseModel):
    type: str = Field(..., pattern="^(violation|warning|info|success)$")
    title: str = Field(..., min_length=1, max_length=200)
    message: Optional[str] = None
    camera_id: Optional[int] = None
    zone_id: Optional[int] = None
    violation_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime | None) -> str:
        """将UTC时间转换为本地时间字符串"""
        if value is None:
            return ""
        # 如果是naive datetime（无时区信息），假设为UTC
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        # 转换为本地时间
        local_time = value.astimezone()
        return local_time.strftime('%Y-%m-%d %H:%M:%S')

    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    total: int
    unread_count: int
    items: list[NotificationResponse]
