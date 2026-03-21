# backend/management/routers/camera.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from management.database import get_db
from management.schemas.camera import (
    CameraCreate, CameraUpdate, CameraResponse, CameraTestRequest, CameraTestResponse
)
from management.services.camera_service import CameraService

router = APIRouter(prefix="/api/cameras", tags=["cameras"])

@router.get("", response_model=List[CameraResponse])
def get_cameras(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取摄像头列表"""
    cameras = CameraService.get_cameras(db, skip, limit)
    return cameras

@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    """获取单个摄像头"""
    camera = CameraService.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="摄像头不存在"
        )
    return camera

@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    """创建摄像头"""
    return CameraService.create_camera(db, camera)

@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    camera: CameraUpdate,
    db: Session = Depends(get_db)
):
    """更新摄像头"""
    updated_camera = CameraService.update_camera(db, camera_id, camera)
    if not updated_camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="摄像头不存在"
        )
    return updated_camera

@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    """删除摄像头"""
    success = CameraService.delete_camera(db, camera_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="摄像头不存在"
        )
    return None

@router.post("/test", response_model=CameraTestResponse)
def test_connection(request: CameraTestRequest):
    """测试视频流连接"""
    result = CameraService.test_connection(request.source_type, request.source_url)
    return result
