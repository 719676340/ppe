# backend/management/routers/notification.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from management.database import get_db
from management.schemas.notification import (
    NotificationCreate, NotificationResponse, NotificationListResponse
)
from management.services.notification_service import NotificationService

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("", response_model=NotificationListResponse)
def get_notifications(
    unread_only: bool = Query(False),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    """获取通知列表"""
    notifications, total = NotificationService.get_notifications(
        db, unread_only, skip, limit
    )
    unread_count = NotificationService.get_unread_count(db)
    return NotificationListResponse(
        total=total,
        unread_count=unread_count,
        items=notifications
    )

@router.get("/unread-count")
def get_unread_count(db: Session = Depends(get_db)):
    """获取未读通知数量"""
    count = NotificationService.get_unread_count(db)
    return {"count": count}

@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    """创建通知"""
    return NotificationService.create_notification(db, notification)

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    """标记通知为已读"""
    notification = NotificationService.mark_as_read(db, notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    return notification

@router.post("/mark-all-read")
def mark_all_notifications_read(db: Session = Depends(get_db)):
    """全部标记为已读"""
    count = NotificationService.mark_all_as_read(db)
    return {"updated": count}

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    """删除通知"""
    success = NotificationService.delete_notification(db, notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    return None

@router.delete("/old", status_code=status.HTTP_204_NO_CONTENT)
def clear_old_notifications(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """清理旧通知"""
    count = NotificationService.clear_old_notifications(db, days)
    return {"deleted": count}
