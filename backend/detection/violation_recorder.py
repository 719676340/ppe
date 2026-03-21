# backend/detection/violation_recorder.py
import cv2
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class ViolationRecorder:
    """违规记录器 - 处理违规检测和记录"""

    def __init__(self, upload_dir: str = "./static/uploads"):
        """
        初始化违规记录器

        Args:
            upload_dir: 违规截图保存目录
        """
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

        # 去重缓存 {camera_id: {zone_id: [(center_x, center_y, timestamp), ...]}}
        self.dedup_cache = defaultdict(lambda: defaultdict(list))

        # 默认去重时间间隔（秒）
        self.dedup_interval = 300  # 5分钟
        self.max_distance = 200  # 像素

    def set_dedup_interval(self, interval: int):
        """设置去重时间间隔"""
        self.dedup_interval = max(0, min(3600, interval))

    def set_max_distance(self, distance: int):
        """设置最大距离"""
        self.max_distance = max(50, min(500, distance))

    def record_violation(
        self,
        camera_id: int,
        zone_id: int,
        frame,
        detection: Dict
    ):
        """
        记录违规

        Args:
            camera_id: 摄像头ID
            zone_id: 区域ID
            frame: 视频帧
            detection: 检测结果
        """
        # 检查是否重复
        bbox = detection['bbox']
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2

        if self._is_duplicate(camera_id, zone_id, center_x, center_y):
            return

        # 保存截图
        image_path = self._save_violation_image(camera_id, zone_id, frame, bbox)

        # 保存到数据库
        try:
            from management.database import SessionLocal, Violation
            db = SessionLocal()

            violation = Violation(
                camera_id=camera_id,
                zone_id=zone_id,
                violation_time=datetime.now(),
                image_path=image_path,
                is_processed=False
            )

            db.add(violation)
            db.commit()
            db.close()

            # 添加到去重缓存
            self._add_to_cache(camera_id, zone_id, center_x, center_y)

            logger.info(f"记录违规: 摄像头{camera_id}, 区域{zone_id}")

            # TODO: 发送违规通知
            # self._send_violation_notification(violation)

        except Exception as e:
            logger.error(f"保存违规记录失败: {e}")

    def _is_duplicate(
        self,
        camera_id: int,
        zone_id: int,
        center_x: float,
        center_y: float
    ) -> bool:
        """检查是否重复"""
        now = datetime.now()
        cache_list = self.dedup_cache[camera_id][zone_id]

        # 清理过期记录
        cutoff_time = now - timedelta(seconds=self.dedup_interval)
        self.dedup_cache[camera_id][zone_id] = [
            (x, y, t) for x, y, t in cache_list if t > cutoff_time
        ]

        # 检查是否有相近的记录
        for x, y, t in self.dedup_cache[camera_id][zone_id]:
            distance = ((center_x - x) ** 2 + (center_y - y) ** 2) ** 0.5
            if distance < self.max_distance:
                return True

        return False

    def _add_to_cache(self, camera_id: int, zone_id: int, x: float, y: float):
        """添加到去重缓存"""
        self.dedup_cache[camera_id][zone_id].append((x, y, datetime.now()))

    def _save_violation_image(
        self,
        camera_id: int,
        zone_id: int,
        frame,
        bbox: list
    ) -> str:
        """保存违规截图"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"violation_cam{camera_id}_zone{zone_id}_{timestamp}.jpg"
        filepath = os.path.join(self.upload_dir, filename)

        # 绘制检测框
        frame_copy = frame.copy()
        x1, y1, x2, y2 = [int(v) for v in bbox]
        cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # 保存图片
        cv2.imwrite(filepath, frame_copy)

        return f"/static/uploads/{filename}"

    def clear_cache(self, camera_id: Optional[int] = None):
        """清空去重缓存"""
        if camera_id is None:
            self.dedup_cache.clear()
        else:
            self.dedup_cache[camera_id].clear()
