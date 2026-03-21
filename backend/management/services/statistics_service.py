# backend/management/services/statistics_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from management.database import Violation, Camera, DetectionZone
from management.schemas.statistics import (
    ZoneStatisticsResponse, PeriodStatisticsResponse,
    CameraStatisticsResponse, TrendDataPoint, TrendStatisticsResponse
)
from typing import List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StatisticsService:
    @staticmethod
    def get_zone_statistics(db: Session, start_time: datetime, end_time: datetime) -> List[ZoneStatisticsResponse]:
        """获取区域统计"""
        results = db.query(
            DetectionZone.id.label('zone_id'),
            DetectionZone.name.label('zone_name'),
            Camera.id.label('camera_id'),
            Camera.name.label('camera_name'),
            func.count(Violation.id).label('violation_count')
        ).join(
            Camera, DetectionZone.camera_id == Camera.id
        ).outerjoin(
            Violation, DetectionZone.id == Violation.zone_id
        ).filter(
            Violation.violation_time >= start_time,
            Violation.violation_time <= end_time
        ).group_by(
            DetectionZone.id, DetectionZone.name, Camera.id, Camera.name
        ).all()

        return [
            ZoneStatisticsResponse(
                zone_id=r.zone_id,
                zone_name=r.zone_name,
                camera_id=r.camera_id,
                camera_name=r.camera_name,
                violation_count=r.violation_count
            )
            for r in results
        ]

    @staticmethod
    def get_period_statistics(db: Session, start_time: datetime, end_time: datetime) -> List[PeriodStatisticsResponse]:
        """获取时段统计"""
        results = db.query(
            func.strftime('%H', Violation.violation_time).label('hour'),
            func.count(Violation.id).label('violation_count')
        ).filter(
            Violation.violation_time >= start_time,
            Violation.violation_time <= end_time
        ).group_by(
            func.strftime('%H', Violation.violation_time)
        ).all()

        # 转换为时段
        period_data = {'morning': 0, 'afternoon': 0, 'night': 0}
        for r in results:
            hour = int(r.hour)
            if 6 <= hour < 12:
                period_data['morning'] += r.violation_count
            elif 12 <= hour < 18:
                period_data['afternoon'] += r.violation_count
            else:
                period_data['night'] += r.violation_count

        return [
            PeriodStatisticsResponse(period=k, violation_count=v)
            for k, v in period_data.items()
        ]

    @staticmethod
    def get_camera_statistics(db: Session, start_time: datetime, end_time: datetime) -> List[CameraStatisticsResponse]:
        """获取摄像头统计"""
        results = db.query(
            Camera.id.label('camera_id'),
            Camera.name.label('camera_name'),
            func.count(Violation.id).label('violation_count')
        ).outerjoin(
            Violation, Camera.id == Violation.camera_id
        ).filter(
            Violation.violation_time >= start_time,
            Violation.violation_time <= end_time
        ).group_by(
            Camera.id, Camera.name
        ).all()

        return [
            CameraStatisticsResponse(
                camera_id=r.camera_id,
                camera_name=r.camera_name,
                violation_count=r.violation_count
            )
            for r in results
        ]

    @staticmethod
    def get_trend_statistics(
        db: Session,
        start_time: datetime,
        end_time: datetime,
        group_by: str = 'day'
    ) -> TrendStatisticsResponse:
        """获取趋势统计"""
        if group_by == 'day':
            date_format = '%Y-%m-%d'
        elif group_by == 'week':
            date_format = '%Y-W%W'
        else:  # month
            date_format = '%Y-%m'

        results = db.query(
            func.strftime(date_format, Violation.violation_time).label('date'),
            func.count(Violation.id).label('count')
        ).filter(
            Violation.violation_time >= start_time,
            Violation.violation_time <= end_time
        ).group_by(
            func.strftime(date_format, Violation.violation_time)
        ).order_by(
            func.strftime(date_format, Violation.violation_time)
        ).all()

        return TrendStatisticsResponse(
            data=[
                TrendDataPoint(date=r.date, count=r.count)
                for r in results
            ]
        )
