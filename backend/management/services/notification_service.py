# backend/management/services/notification_service.py
from sqlalchemy.orm import Session
from management.database import Notification
from management.schemas.notification import NotificationCreate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def get_notifications(
        db: Session,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Notification], int]:
        """获取通知列表"""
        query = db.query(Notification)

        if unread_only:
            query = query.filter(Notification.is_read == False)

        total = query.count()
        notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

        return notifications, total

    @staticmethod
    def get_unread_count(db: Session) -> int:
        """获取未读数量"""
        return db.query(Notification).filter(Notification.is_read == False).count()

    @staticmethod
    def create_notification(db: Session, notification: NotificationCreate) -> Notification:
        """创建通知"""
        db_notification = Notification(**notification.model_dump())
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification

    @staticmethod
    def mark_as_read(db: Session, notification_id: int) -> Optional[Notification]:
        """标记为已读"""
        db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not db_notification:
            return None

        db_notification.is_read = True
        db.commit()
        db.refresh(db_notification)
        return db_notification

    @staticmethod
    def mark_all_as_read(db: Session) -> int:
        """全部标记为已读"""
        count = db.query(Notification).filter(Notification.is_read == False).update(
            {"is_read": True}
        )
        db.commit()
        return count

    @staticmethod
    def delete_notification(db: Session, notification_id: int) -> bool:
        """删除通知"""
        db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not db_notification:
            return False

        db.delete(db_notification)
        db.commit()
        return True

    @staticmethod
    def clear_old_notifications(db: Session, days: int = 30) -> int:
        """清理旧通知"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)

        count = db.query(Notification).filter(
            Notification.created_at < cutoff_date,
            Notification.is_read == True
        ).delete()

        db.commit()
        return count
