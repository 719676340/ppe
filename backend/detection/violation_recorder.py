# backend/detection/violation_recorder.py
import cv2
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class ViolationRecorder:
    """违规记录器 - 处理违规检测和记录"""

    def __init__(self, upload_dir: str = "./static/uploads", dedup_interval: int = 30, max_distance: int = 100):
        """
        初始化违规记录器

        Args:
            upload_dir: 违规截图保存目录
            dedup_interval: 去重时间间隔（秒），默认30秒
            max_distance: 判定为同一位置的最大距离（像素），默认100像素
        """
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

        # 去重缓存 {camera_id: {zone_id: [(center_x, center_y, timestamp), ...]}}
        self.dedup_cache = defaultdict(lambda: defaultdict(list))

        # 去重配置参数
        self.dedup_interval = dedup_interval  # 默认30秒
        self.max_distance = max_distance  # 默认100像素

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
        logger.info(f"[VIOLATION] ===== 开始记录违规: 摄像头{camera_id}, 区域{zone_id} =====")
        logger.info(f"[VIOLATION] 检测结果: class={detection.get('class_name')}, is_violation={detection.get('is_violation')}, confidence={detection.get('confidence')}")

        # 检查是否重复
        bbox = detection['bbox']
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2

        is_dup = self._is_duplicate(camera_id, zone_id, center_x, center_y)
        logger.info(f"[VIOLATION] 去重检查结果: {is_dup}, 中心点=({center_x:.1f}, {center_y:.1f})")

        if is_dup:
            logger.info(f"[VIOLATION] 重复违规被过滤: 摄像头{camera_id}, 区域{zone_id}")
            return

        logger.info(f"[VIOLATION] 通过去重检查，准备保存截图")

        # 保存截图
        try:
            image_path = self._save_violation_image(camera_id, zone_id, frame, bbox)
            logger.info(f"[VIOLATION] 截图已保存: {image_path}")
        except Exception as e:
            logger.error(f"[VIOLATION] 保存截图失败: {e}", exc_info=True)
            return

        # 保存到数据库
        try:
            from management.database import SessionLocal, Violation
            db = SessionLocal()

            try:
                violation = Violation(
                    camera_id=camera_id,
                    zone_id=zone_id,
                    violation_time=datetime.now(timezone.utc),
                    image_path=image_path,
                    is_processed=False
                )

                db.add(violation)
                db.flush()  # 刷新以获取ID
                db.commit()

                logger.info(f"[VIOLATION] 数据库提交成功，violation_id={violation.id}")

                # 添加到去重缓存
                self._add_to_cache(camera_id, zone_id, center_x, center_y)

                # 创建通知记录
                try:
                    from management.database import Notification, DetectionZone
                    zone = db.query(DetectionZone).filter(DetectionZone.id == zone_id).first()
                    zone_name = zone.name if zone else f"区域{zone_id}"

                    notification = Notification(
                        type="violation",
                        title=f"检测到未佩戴PPE违规",
                        message=f"摄像头 {camera_id} 的 {zone_name} 检测到未佩戴PPE违规",
                        camera_id=camera_id,
                        zone_id=zone_id,
                        violation_id=violation.id,
                        is_read=False
                    )
                    db.add(notification)
                    db.commit()
                    logger.info(f"[VIOLATION] 通知记录已创建，notification_id={notification.id}")
                except Exception as e:
                    db.rollback()
                    logger.error(f"[VIOLATION] 创建通知记录失败: {e}", exc_info=True)
                logger.info(f"[VIOLATION] 已添加到去重缓存")

                logger.info(f"[VIOLATION] ===== 成功保存违规记录: 摄像头{camera_id}, 区域{zone_id} =====")

            except Exception as e:
                db.rollback()
                logger.error(f"[VIOLATION] 数据库操作失败，已回滚: {e}", exc_info=True)
                raise
            finally:
                db.close()

            # TODO: 发送违规通知
            # self._send_violation_notification(violation)

        except Exception as e:
            logger.error(f"[VIOLATION] 保存违规记录失败: {e}", exc_info=True)

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

        logger.info(f"[VIOLATION] 去重检查: camera_id={camera_id}, zone_id={zone_id}, 当前缓存数量={len(cache_list)}")

        # 清理过期记录（超过5分钟）
        cutoff_time = now - timedelta(seconds=self.dedup_interval)
        self.dedup_cache[camera_id][zone_id] = [
            (x, y, t) for x, y, t in cache_list if t > cutoff_time
        ]

        cleaned_cache = self.dedup_cache[camera_id][zone_id]
        logger.info(f"[VIOLATION] 清理过期后缓存数量={len(cleaned_cache)}")

        # 检查是否有相近的记录
        for idx, (x, y, t) in enumerate(cleaned_cache):
            distance = ((center_x - x) ** 2 + (center_y - y) ** 2) ** 0.5
            logger.info(f"[VIOLATION] 对比缓存记录{idx+1}: 缓存位置=({x:.1f},{y:.1f}), 当前位置=({center_x:.1f},{center_y:.1f}), 距离={distance:.1f}, 阈值={self.max_distance}")
            if distance < self.max_distance:
                logger.info(f"[VIOLATION] 找到相近记录，判断为重复")
                return True

        logger.info(f"[VIOLATION] 未找到相近记录，不是重复")
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
