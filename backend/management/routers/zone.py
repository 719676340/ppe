# backend/management/routers/zone.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from management.database import get_db
from management.schemas.zone import (
    DetectionZoneCreate, DetectionZoneUpdate, DetectionZoneResponse
)
from management.services.zone_service import ZoneService

router = APIRouter(prefix="/api/zones", tags=["zones"])

@router.get("", response_model=List[DetectionZoneResponse])
def get_zones(
    camera_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取检测区域列表"""
    zones = ZoneService.get_zones(db, camera_id, skip, limit)
    return zones

@router.get("/{zone_id}", response_model=DetectionZoneResponse)
def get_zone(zone_id: int, db: Session = Depends(get_db)):
    """获取单个检测区域"""
    zone = ZoneService.get_zone(db, zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="检测区域不存在"
        )
    return zone

@router.post("", response_model=DetectionZoneResponse, status_code=status.HTTP_201_CREATED)
def create_zone(zone: DetectionZoneCreate, db: Session = Depends(get_db)):
    """创建检测区域"""
    return ZoneService.create_zone(db, zone)

@router.put("/{zone_id}", response_model=DetectionZoneResponse)
def update_zone(
    zone_id: int,
    zone: DetectionZoneUpdate,
    db: Session = Depends(get_db)
):
    """更新检测区域"""
    updated_zone = ZoneService.update_zone(db, zone_id, zone)
    if not updated_zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="检测区域不存在"
        )
    return updated_zone

@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(zone_id: int, db: Session = Depends(get_db)):
    """删除检测区域"""
    success = ZoneService.delete_zone(db, zone_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="检测区域不存在"
        )
    return None
