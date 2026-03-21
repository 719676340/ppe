# backend/management/services/camera_service.py
from sqlalchemy.orm import Session
from management.database import Camera, DetectionZone
from management.schemas.camera import CameraCreate, CameraUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class CameraService:
    @staticmethod
    def get_cameras(db: Session, skip: int = 0, limit: int = 100) -> List[Camera]:
        """获取摄像头列表"""
        return db.query(Camera).offset(skip).limit(limit).all()

    @staticmethod
    def get_camera(db: Session, camera_id: int) -> Optional[Camera]:
        """获取单个摄像头"""
        return db.query(Camera).filter(Camera.id == camera_id).first()

    @staticmethod
    def create_camera(db: Session, camera: CameraCreate) -> Camera:
        """创建摄像头"""
        db_camera = Camera(**camera.model_dump())
        db.add(db_camera)
        db.commit()
        db.refresh(db_camera)
        return db_camera

    @staticmethod
    def update_camera(db: Session, camera_id: int, camera: CameraUpdate) -> Optional[Camera]:
        """更新摄像头"""
        db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if not db_camera:
            return None

        for field, value in camera.model_dump(exclude_unset=True).items():
            setattr(db_camera, field, value)

        db.commit()
        db.refresh(db_camera)
        return db_camera

    @staticmethod
    def delete_camera(db: Session, camera_id: int) -> bool:
        """删除摄像头"""
        db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if not db_camera:
            return False

        db.delete(db_camera)
        db.commit()
        return True

    @staticmethod
    def test_connection(source_type: str, source_url: str) -> dict:
        """测试视频流连接"""
        import cv2

        try:
            cap = cv2.VideoCapture(source_url)
            if not cap.isOpened():
                return {"success": False, "message": "无法连接到视频源"}

            ret, frame = cap.read()
            if not ret:
                cap.release()
                return {"success": False, "message": "无法读取视频帧"}

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            cap.release()

            return {
                "success": True,
                "message": "连接成功",
                "resolution": f"{width}x{height}",
                "fps": fps
            }

        except Exception as e:
            logger.error(f"测试连接失败: {e}")
            return {"success": False, "message": f"测试失败: {str(e)}"}
