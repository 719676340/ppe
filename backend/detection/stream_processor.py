# backend/detection/stream_processor.py
import cv2
import threading
import time
import numpy as np
from queue import Queue
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StreamProcessor:
    """视频流处理器 - 支持RTSP/RTMP/本地视频文件"""

    def __init__(
        self,
        source_url: str,
        camera_id: int,
        detector,
        roi_manager,
        violation_recorder,
        on_detection_callback: Optional[Callable] = None
    ):
        """
        初始化视频流处理器

        Args:
            source_url: 视频流地址 (RTSP/RTMP/本地文件)
            camera_id: 摄像头ID
            detector: 检测器实例 (PPEDetector)
            roi_manager: ROI管理器实例
            violation_recorder: 违规记录器实例
            on_detection_callback: 检测回调函数
        """
        self.source_url = source_url
        self.camera_id = camera_id
        self.detector = detector
        self.roi_manager = roi_manager
        self.violation_recorder = violation_recorder
        self.on_detection_callback = on_detection_callback

        self.running = False
        self.thread = None
        self.cap = None
        self.frame_queue = Queue(maxsize=30)  # 保存最近30帧

        # 断线检测
        self.last_frame_time = None
        self.is_online = True
        self.reconnect_attempts = 0
        self.reconnect_interval = 5  # 秒

    def start(self):
        """启动视频流处理"""
        if self.running:
            logger.warning(f"摄像头 {self.camera_id} 已在运行中")
            return

        self.running = True
        self.thread = threading.Thread(target=self._process_stream, daemon=True)
        self.thread.start()
        logger.info(f"摄像头 {self.camera_id} 视频流处理已启动: {self.source_url}")

    def stop(self):
        """停止视频流处理"""
        logger.info(f"正在停止摄像头 {self.camera_id} 的视频流处理...")
        self.running = False

        if self.thread:
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                logger.warning(f"摄像头 {self.camera_id} 线程未能正常退出")

        if self.cap:
            self.cap.release()
            self.cap = None

        logger.info(f"摄像头 {self.camera_id} 视频流处理已停止")

    def _connect_stream(self) -> Optional[cv2.VideoCapture]:
        """连接视频流"""
        try:
            logger.info(f"尝试连接视频流: {self.source_url}")
            cap = cv2.VideoCapture(self.source_url)

            if not cap.isOpened():
                logger.error(f"无法连接到视频流: {self.source_url}")
                return None

            # 设置缓冲区大小以减少延迟
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            # 尝试读取第一帧以验证连接
            ret, frame = cap.read()
            if not ret or frame is None:
                logger.error(f"视频流 {self.source_url} 无法读取帧")
                cap.release()
                return None

            logger.info(f"成功连接到视频流: {self.source_url}, 分辨率: {frame.shape[1]}x{frame.shape[0]}")
            return cap

        except Exception as e:
            logger.error(f"连接视频流时出错: {e}")
            return None

    def _process_stream(self):
        """处理视频流的主循环"""
        while self.running:
            # 如果没有连接，尝试连接
            if self.cap is None:
                self.cap = self._connect_stream()

                if self.cap is None:
                    self._handle_disconnect()
                    time.sleep(self.reconnect_interval)
                    continue

                # 连接成功后的处理
                if not self.is_online:
                    self._handle_reconnect()

            # 读取帧
            ret, frame = self.cap.read()

            if not ret or frame is None:
                self._handle_disconnect()
                self.cap.release()
                self.cap = None
                time.sleep(2)
                continue

            # 连接正常
            self.last_frame_time = datetime.now()

            # 将帧放入队列（非阻塞）
            if not self.frame_queue.full():
                try:
                    self.frame_queue.put_nowait(frame)
                except:
                    pass  # 队列满，丢弃旧帧

            # 执行检测（每秒处理约5次以节省资源）
            self._detect_frame(frame)

            # 控制处理频率
            time.sleep(0.2)  # 约5fps的处理频率

    def _detect_frame(self, frame):
        """对单帧进行检测"""
        try:
            # 获取该摄像头的所有启用的检测区域
            from management.database import SessionLocal, DetectionZone
            db = SessionLocal()

            try:
                zones = db.query(DetectionZone).filter(
                    DetectionZone.camera_id == self.camera_id,
                    DetectionZone.enabled == True
                ).all()
            finally:
                db.close()

            if not zones:
                return  # 没有配置检测区域，跳过检测

            # 执行检测
            detections = self.detector.detect(frame)

            # 处理每个区域
            for zone in zones:
                try:
                    zone_coords = self.roi_manager.parse_coordinates(zone.coordinates)
                    height, width = frame.shape[:2]
                    scaled_coords = self.roi_manager.scale_coordinates(
                        zone_coords, width, height
                    )

                    # 检查每个检测是否在区域内
                    for detection in detections:
                        if self.roi_manager.is_bbox_in_zone(detection['bbox'], scaled_coords):
                            # 在区域内，检查是否违规
                            if detection.get('is_violation', False):
                                # 记录违规
                                self.violation_recorder.record_violation(
                                    self.camera_id,
                                    zone.id,
                                    frame,
                                    detection
                                )

                                # 调用回调函数
                                if self.on_detection_callback:
                                    self.on_detection_callback({
                                        'camera_id': self.camera_id,
                                        'zone_id': zone.id,
                                        'zone_name': zone.name,
                                        'detection': detection,
                                        'timestamp': datetime.now()
                                    })
                except Exception as e:
                    logger.error(f"处理区域 {zone.id} 时出错: {e}")

        except Exception as e:
            logger.error(f"检测帧时出错: {e}")

    def _handle_disconnect(self):
        """处理断线"""
        if self.is_online:
            self.is_online = False
            self.reconnect_attempts += 1
            logger.warning(f"摄像头 {self.camera_id} 断线 (尝试 {self.reconnect_attempts} 次)")

    def _handle_reconnect(self):
        """处理重连成功"""
        self.is_online = True
        self.reconnect_attempts = 0
        logger.info(f"摄像头 {self.camera_id} 重连成功")

    def get_latest_frame(self) -> Optional[np.ndarray]:
        """获取最新帧"""
        try:
            if not self.frame_queue.empty():
                return self.frame_queue.get_nowait()
        except:
            pass
        return None

    def get_status(self) -> Dict[str, Any]:
        """获取处理器状态"""
        return {
            "camera_id": self.camera_id,
            "source_url": self.source_url,
            "is_online": self.is_online,
            "is_running": self.running,
            "reconnect_attempts": self.reconnect_attempts,
            "last_frame_time": self.last_frame_time.isoformat() if self.last_frame_time else None
        }
