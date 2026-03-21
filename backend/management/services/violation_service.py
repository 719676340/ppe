# backend/management/services/violation_service.py
from sqlalchemy.orm import Session
from management.database import Violation
from management.schemas.violation import ViolationFilter
from typing import List, Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ViolationService:
    @staticmethod
    def get_violations(
        db: Session,
        camera_id: Optional[int] = None,
        zone_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        is_processed: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Violation], int]:
        """获取违规记录列表"""
        query = db.query(Violation)

        if camera_id is not None:
            query = query.filter(Violation.camera_id == camera_id)
        if zone_id is not None:
            query = query.filter(Violation.zone_id == zone_id)
        if start_time is not None:
            query = query.filter(Violation.violation_time >= start_time)
        if end_time is not None:
            query = query.filter(Violation.violation_time <= end_time)
        if is_processed is not None:
            query = query.filter(Violation.is_processed == is_processed)

        total = query.count()
        violations = query.order_by(Violation.violation_time.desc()).offset(skip).limit(limit).all()

        return violations, total

    @staticmethod
    def get_violation(db: Session, violation_id: int) -> Optional[Violation]:
        """获取单个违规记录"""
        return db.query(Violation).filter(Violation.id == violation_id).first()

    @staticmethod
    def update_violation_remark(db: Session, violation_id: int, remark: str) -> Optional[Violation]:
        """更新违规备注"""
        db_violation = db.query(Violation).filter(Violation.id == violation_id).first()
        if not db_violation:
            return None

        db_violation.remark = remark
        db.commit()
        db.refresh(db_violation)
        return db_violation

    @staticmethod
    def mark_as_processed(db: Session, violation_id: int) -> Optional[Violation]:
        """标记为已处理"""
        db_violation = db.query(Violation).filter(Violation.id == violation_id).first()
        if not db_violation:
            return None

        db_violation.is_processed = True
        db.commit()
        db.refresh(db_violation)
        return db_violation

    @staticmethod
    def delete_violation(db: Session, violation_id: int) -> bool:
        """删除违规记录"""
        db_violation = db.query(Violation).filter(Violation.id == violation_id).first()
        if not db_violation:
            return False

        db.delete(db_violation)
        db.commit()
        return True

    @staticmethod
    def batch_mark_processed(db: Session, violation_ids: List[int]) -> int:
        """批量标记为已处理"""
        count = db.query(Violation).filter(Violation.id.in_(violation_ids)).update(
            {"is_processed": True}
        )
        db.commit()
        return count
