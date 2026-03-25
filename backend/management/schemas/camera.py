# backend/management/schemas/camera.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CameraBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    source_type: str = Field(..., pattern="^(rtsp|file|usb)$")
    source_url: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    status: str = Field("active", pattern="^(active|inactive)$")
    enabled: bool = Field(False, description="是否启用后台检测")

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    source_type: Optional[str] = Field(None, pattern="^(rtsp|file|usb)$")
    source_url: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
    enabled: Optional[bool] = Field(None, description="是否启用后台检测")

class CameraResponse(CameraBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CameraTestRequest(BaseModel):
    source_type: str = Field(..., pattern="^(rtsp|file|usb)$")
    source_url: str

class CameraTestResponse(BaseModel):
    success: bool
    message: str
    resolution: Optional[str] = None
    fps: Optional[float] = None
