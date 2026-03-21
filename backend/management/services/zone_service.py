# backend/management/services/zone_service.py
from sqlalchemy.orm import Session
from management.database import DetectionZone
from management.schemas.zone import DetectionZoneCreate, DetectionZoneUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class ZoneService:
    @staticmethod
    def get_zones(db: Session, camera_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[DetectionZone]:
        """获取检测区域列表"""
        query = db.query(DetectionZone)
        if camera_id is not None:
            query = query.filter(DetectionZone.camera_id == camera_id)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_zone(db: Session, zone_id: int) -> Optional[DetectionZone]:
        """获取单个检测区域"""
        return db.query(DetectionZone).filter(DetectionZone.id == zone_id).first()

    @staticmethod
    def create_zone(db: Session, zone: DetectionZoneCreate) -> DetectionZone:
        """创建检测区域"""
        db_zone = DetectionZone(**zone.model_dump())
        db.add(db_zone)
        db.commit()
        db.refresh(db_zone)
        return db_zone

    @staticmethod
    def update_zone(db: Session, zone_id: int, zone: DetectionZoneUpdate) -> Optional[DetectionZone]:
        """更新检测区域"""
        db_zone = db.query(DetectionZone).filter(DetectionZone.id == zone_id).first()
        if not db_zone:
            return None

        for field, value in zone.model_dump(exclude_unset=True).items():
            setattr(db_zone, field, value)

        db.commit()
        db.refresh(db_zone)
        return db_zone

    @staticmethod
    def delete_zone(db: Session, zone_id: int) -> bool:
        """删除检测区域"""
        db_zone = db.query(DetectionZone).filter(DetectionZone.id == zone_id).first()
        if not db_zone:
            return False

        db.delete(db_zone)
        db.commit()
        return True
