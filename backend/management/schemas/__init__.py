# backend/management/schemas/__init__.py
from .camera import (
    CameraBase, CameraCreate, CameraUpdate, CameraResponse,
    CameraTestRequest, CameraTestResponse
)
from .zone import (
    DetectionZoneBase, DetectionZoneCreate, DetectionZoneUpdate,
    DetectionZoneResponse
)
from .violation import (
    ViolationBase, ViolationResponse, ViolationListResponse,
    ViolationFilter
)
from .statistics import (
    ZoneStatisticsResponse, PeriodStatisticsResponse,
    CameraStatisticsResponse, TrendDataPoint, TrendStatisticsResponse
)
from .notification import (
    NotificationBase, NotificationCreate, NotificationResponse,
    NotificationListResponse
)

__all__ = [
    'CameraBase', 'CameraCreate', 'CameraUpdate', 'CameraResponse',
    'CameraTestRequest', 'CameraTestResponse',
    'DetectionZoneBase', 'DetectionZoneCreate', 'DetectionZoneUpdate',
    'DetectionZoneResponse',
    'ViolationBase', 'ViolationResponse', 'ViolationListResponse',
    'ViolationFilter',
    'ZoneStatisticsResponse', 'PeriodStatisticsResponse',
    'CameraStatisticsResponse', 'TrendDataPoint', 'TrendStatisticsResponse',
    'NotificationBase', 'NotificationCreate', 'NotificationResponse',
    'NotificationListResponse'
]
