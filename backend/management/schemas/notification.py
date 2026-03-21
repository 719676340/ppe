# backend/management/schemas/notification.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

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

    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    total: int
    unread_count: int
    items: list[NotificationResponse]
