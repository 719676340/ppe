# backend/management/routers/violation.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from management.database import get_db
from management.schemas.violation import ViolationResponse, ViolationListResponse
from management.services.violation_service import ViolationService

router = APIRouter(prefix="/api/violations", tags=["violations"])

@router.get("", response_model=ViolationListResponse)
def get_violations(
    camera_id: Optional[int] = None,
    zone_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    is_processed: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取违规记录列表"""
    skip = (page - 1) * page_size
    violations, total = ViolationService.get_violations(
        db, camera_id, zone_id, start_time, end_time, is_processed, skip, page_size
    )
    return ViolationListResponse(total=total, items=violations)

@router.get("/{violation_id}", response_model=ViolationResponse)
def get_violation(violation_id: int, db: Session = Depends(get_db)):
    """获取单个违规记录"""
    violation = ViolationService.get_violation(db, violation_id)
    if not violation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="违规记录不存在"
        )
    return violation

@router.patch("/{violation_id}/remark", response_model=ViolationResponse)
def update_violation_remark(
    violation_id: int,
    remark: str,
    db: Session = Depends(get_db)
):
    """更新违规备注"""
    violation = ViolationService.update_violation_remark(db, violation_id, remark)
    if not violation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="违规记录不存在"
        )
    return violation

@router.patch("/{violation_id}/process", response_model=ViolationResponse)
def mark_violation_processed(violation_id: int, db: Session = Depends(get_db)):
    """标记违规为已处理"""
    violation = ViolationService.mark_as_processed(db, violation_id)
    if not violation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="违规记录不存在"
        )
    return violation

@router.delete("/{violation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_violation(violation_id: int, db: Session = Depends(get_db)):
    """删除违规记录"""
    success = ViolationService.delete_violation(db, violation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="违规记录不存在"
        )
    return None

@router.post("/batch-process", response_model=dict)
def batch_mark_violations_processed(
    violation_ids: List[int],
    db: Session = Depends(get_db)
):
    """批量标记违规为已处理"""
    count = ViolationService.batch_mark_processed(db, violation_ids)
    return {"updated": count}
