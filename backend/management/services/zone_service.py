# backend/management/services/zone_service.py
from sqlalchemy.orm import Session
from management.database import DetectionZone, Camera
from management.schemas.zone import DetectionZoneCreate, DetectionZoneUpdate
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ZoneService:
    @staticmethod
    def get_zones(db: Session, camera_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """获取检测区域列表"""
        query = db.query(
            DetectionZone.id,
            DetectionZone.camera_id,
            DetectionZone.name,
            DetectionZone.coordinates,
            DetectionZone.enabled,
            DetectionZone.created_at,
            Camera.name.label('camera_name')
        ).join(Camera, DetectionZone.camera_id == Camera.id)

        if camera_id is not None:
            query = query.filter(DetectionZone.camera_id == camera_id)

        results = query.offset(skip).limit(limit).all()

        # 转换为字典列表
        return [
            {
                "id": row.id,
                "camera_id": row.camera_id,
                "camera_name": row.camera_name,
                "name": row.name,
                "coordinates": row.coordinates,
                "enabled": row.enabled,
                "created_at": row.created_at
            }
            for row in results
        ]

    @staticmethod
    def get_zone(db: Session, zone_id: int) -> Optional[Dict[str, Any]]:
        """获取单个检测区域"""
        result = db.query(
            DetectionZone.id,
            DetectionZone.camera_id,
            DetectionZone.name,
            DetectionZone.coordinates,
            DetectionZone.enabled,
            DetectionZone.created_at,
            Camera.name.label('camera_name')
        ).join(Camera, DetectionZone.camera_id == Camera.id).filter(
            DetectionZone.id == zone_id
        ).first()

        if not result:
            return None

        return {
            "id": result.id,
            "camera_id": result.camera_id,
            "camera_name": result.camera_name,
            "name": result.name,
            "coordinates": result.coordinates,
            "enabled": result.enabled,
            "created_at": result.created_at
        }

    @staticmethod
    def create_zone(db: Session, zone: DetectionZoneCreate) -> Dict[str, Any]:
        """创建检测区域"""
        db_zone = DetectionZone(**zone.model_dump())
        db.add(db_zone)
        db.commit()
        db.refresh(db_zone)

        # 获取摄像头名称
        camera = db.query(Camera).filter(Camera.id == db_zone.camera_id).first()

        return {
            "id": db_zone.id,
            "camera_id": db_zone.camera_id,
            "camera_name": camera.name if camera else None,
            "name": db_zone.name,
            "coordinates": db_zone.coordinates,
            "enabled": db_zone.enabled,
            "created_at": db_zone.created_at
        }

    @staticmethod
    def update_zone(db: Session, zone_id: int, zone: DetectionZoneUpdate) -> Optional[Dict[str, Any]]:
        """更新检测区域"""
        db_zone = db.query(DetectionZone).filter(DetectionZone.id == zone_id).first()
        if not db_zone:
            return None

        for field, value in zone.model_dump(exclude_unset=True).items():
            setattr(db_zone, field, value)

        db.commit()
        db.refresh(db_zone)

        # 获取摄像头名称
        camera = db.query(Camera).filter(Camera.id == db_zone.camera_id).first()

        return {
            "id": db_zone.id,
            "camera_id": db_zone.camera_id,
            "camera_name": camera.name if camera else None,
            "name": db_zone.name,
            "coordinates": db_zone.coordinates,
            "enabled": db_zone.enabled,
            "created_at": db_zone.created_at
        }

    @staticmethod
    def delete_zone(db: Session, zone_id: int) -> bool:
        """删除检测区域"""
        db_zone = db.query(DetectionZone).filter(DetectionZone.id == zone_id).first()
        if not db_zone:
            return False

        db.delete(db_zone)
        db.commit()
        return True
