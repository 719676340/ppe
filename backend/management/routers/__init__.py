# backend/management/routers/__init__.py
from .camera import router as camera_router
from .zone import router as zone_router
from .violation import router as violation_router
from .statistics import router as statistics_router
from .notification import router as notification_router

__all__ = [
    'camera_router',
    'zone_router',
    'violation_router',
    'statistics_router',
    'notification_router'
]
