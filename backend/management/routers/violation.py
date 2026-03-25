# backend/management/routers/violation.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pathlib import Path
import io
import logging
import time
from management.database import get_db
from management.schemas.violation import ViolationResponse, ViolationListResponse
from management.services.violation_service import ViolationService

router = APIRouter(prefix="/api/violations", tags=["violations"])

def parse_optional_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """将日期时间字符串解析为datetime（本地时间），然后转换为UTC用于数据库查询"""
    if not date_str:
        return None

    # 尝试多种格式
    formats_to_try = [
        '%Y-%m-%d %H:%M:%S',  # 前端发送的新格式
        '%Y-%m-%dT%H:%M:%S',  # ISO 格式（无时区）
        '%Y-%m-%d',           # 纯日期
        '%Y-%m-%dT%H:%M:%S.%f',  # ISO 格式带微秒
    ]

    for fmt in formats_to_try:
        try:
            dt = datetime.strptime(date_str, fmt)
            # 获取本地时区偏移
            tz_offset = -time.timezone if time.daylight == 0 else -time.altzone
            # 将本地时间转换为UTC
            local_dt = dt.replace(tzinfo=timezone(timedelta(seconds=tz_offset)))
            return local_dt.astimezone(timezone.utc).replace(tzinfo=None)
        except:
            continue

    # 尝试 fromisoformat（处理带 Z 的 UTC 时间）
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    except:
        return None

@router.get("", response_model=ViolationListResponse)
def get_violations(
    camera_id: Optional[int] = None,
    zone_id: Optional[int] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    is_processed: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取违规记录列表"""
    # 解析时间参数（已转换为UTC）
    start_dt = parse_optional_datetime(start_time)
    end_dt = parse_optional_datetime(end_time)

    skip = (page - 1) * page_size
    violations, total = ViolationService.get_violations(
        db, camera_id, zone_id, start_dt, end_dt, is_processed, skip, page_size
    )
    return ViolationListResponse(total=total, items=violations)

@router.get("/export")
def export_violations(
    camera_id: Optional[int] = None,
    zone_id: Optional[int] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    is_processed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """导出违规记录到Excel文件，包含截图"""
    # 解析时间参数（已转换为UTC）
    start_dt = parse_optional_datetime(start_time)
    end_dt = parse_optional_datetime(end_time)

    try:
        # routers -> management -> backend -> project_root
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        excel_data = ViolationService.export_to_excel(
            db, camera_id, zone_id, start_dt, end_dt, is_processed, base_dir
        )

        filename = f"violations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        logging.error(f"导出Excel失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )

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
