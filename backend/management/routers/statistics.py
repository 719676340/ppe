# backend/management/routers/statistics.py
from fastapi import APIRouter, Query, Depends
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from management.database import get_db
from management.schemas.statistics import (
    ZoneStatisticsResponse, PeriodStatisticsResponse,
    CameraStatisticsResponse, TrendStatisticsResponse
)
from management.services.statistics_service import StatisticsService
from typing import List, Optional
import time

router = APIRouter(prefix="/api/statistics", tags=["statistics"])

def parse_datetime(date_str: str) -> datetime:
    """将日期时间字符串解析为datetime（本地时间），然后转换为UTC用于数据库查询"""
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
            tz_offset = -time.timezone if time.daylight == 0 else -time.altzone
            local_dt = dt.replace(tzinfo=timezone(timedelta(seconds=tz_offset)))
            return local_dt.astimezone(timezone.utc).replace(tzinfo=None)
        except:
            continue

    # 尝试 fromisoformat
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    except:
        raise ValueError(f"无法解析日期时间: {date_str}")

@router.get("/zone", response_model=List[ZoneStatisticsResponse])
def get_zone_statistics(
    start_time: str = Query(...),
    end_time: str = Query(...),
    db: Session = Depends(get_db)
):
    """获取区域统计"""
    start_dt = parse_datetime(start_time)
    end_dt = parse_datetime(end_time)
    return StatisticsService.get_zone_statistics(db, start_dt, end_dt)

@router.get("/period", response_model=List[PeriodStatisticsResponse])
def get_period_statistics(
    start_time: str = Query(...),
    end_time: str = Query(...),
    db: Session = Depends(get_db)
):
    """获取时段统计"""
    start_dt = parse_datetime(start_time)
    end_dt = parse_datetime(end_time)
    return StatisticsService.get_period_statistics(db, start_dt, end_dt)

@router.get("/camera", response_model=List[CameraStatisticsResponse])
def get_camera_statistics(
    start_time: str = Query(...),
    end_time: str = Query(...),
    db: Session = Depends(get_db)
):
    """获取摄像头统计"""
    start_dt = parse_datetime(start_time)
    end_dt = parse_datetime(end_time)
    return StatisticsService.get_camera_statistics(db, start_dt, end_dt)

@router.get("/trend", response_model=TrendStatisticsResponse)
def get_trend_statistics(
    start_time: str = Query(...),
    end_time: str = Query(...),
    group_by: str = Query("day", regex="^(day|week|month)$"),
    db: Session = Depends(get_db)
):
    """获取趋势统计"""
    start_dt = parse_datetime(start_time)
    end_dt = parse_datetime(end_time)
    return StatisticsService.get_trend_statistics(db, start_dt, end_dt, group_by)

@router.get("/overview")
def get_statistics_overview(db: Session = Depends(get_db)):
    """获取统计概览"""
    from management.database import Violation, Camera, DetectionZone
    from sqlalchemy import func

    # 今日违规数
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_violations = db.query(func.count(Violation.id)).filter(
        Violation.violation_time >= today
    ).scalar()

    # 本周违规数
    week_ago = datetime.now() - timedelta(days=7)
    week_violations = db.query(func.count(Violation.id)).filter(
        Violation.violation_time >= week_ago
    ).scalar()

    # 总摄像头数
    total_cameras = db.query(func.count(Camera.id)).scalar()

    # 总区域数
    total_zones = db.query(func.count(DetectionZone.id)).scalar()

    return {
        "today_violations": today_violations or 0,
        "week_violations": week_violations or 0,
        "total_cameras": total_cameras or 0,
        "total_zones": total_zones or 0
    }
