# backend/management/routers/statistics.py
from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from management.database import get_db
from management.schemas.statistics import (
    ZoneStatisticsResponse, PeriodStatisticsResponse,
    CameraStatisticsResponse, TrendStatisticsResponse
)
from management.services.statistics_service import StatisticsService
from typing import List

router = APIRouter(prefix="/api/statistics", tags=["statistics"])

@router.get("/zone", response_model=List[ZoneStatisticsResponse])
def get_zone_statistics(
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    db: Session = Depends(get_db)
):
    """获取区域统计"""
    return StatisticsService.get_zone_statistics(db, start_time, end_time)

@router.get("/period", response_model=List[PeriodStatisticsResponse])
def get_period_statistics(
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    db: Session = Depends(get_db)
):
    """获取时段统计"""
    return StatisticsService.get_period_statistics(db, start_time, end_time)

@router.get("/camera", response_model=List[CameraStatisticsResponse])
def get_camera_statistics(
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    db: Session = Depends(get_db)
):
    """获取摄像头统计"""
    return StatisticsService.get_camera_statistics(db, start_time, end_time)

@router.get("/trend", response_model=TrendStatisticsResponse)
def get_trend_statistics(
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    group_by: str = Query("day", regex="^(day|week|month)$"),
    db: Session = Depends(get_db)
):
    """获取趋势统计"""
    return StatisticsService.get_trend_statistics(db, start_time, end_time, group_by)

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
