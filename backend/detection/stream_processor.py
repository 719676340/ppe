# backend/detection/stream_processor.py
import cv2
import threading
import time
import numpy as np
from queue import Queue
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import logging
import asyncio

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
        self.latest_detections = []  # 保存最新的检测结果
        self.detection_frame = None  # 保存带检测框的帧

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
        frame_count = 0  # 帧计数器，用于控制检测频率

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
                time.sleep(0.1)
                continue

            # 连接正常
            self.last_frame_time = datetime.now()
            frame_count += 1

            # 每5帧执行一次检测（降低检测频率以节省资源）
            should_detect = (frame_count % 5) == 0

            if should_detect:
                self._detect_frame(frame)

            # 准备显示的帧：如果有检测结果则绘制检测框
            if self.latest_detections:
                display_frame = self._draw_detections(frame.copy(), self.latest_detections)
            else:
                display_frame = frame

            # 绘制区域边界（如果有配置的区域）
            display_frame = self._draw_zone_boundaries(display_frame)

            # 将帧放入队列（非阻塞）
            if not self.frame_queue.full():
                try:
                    self.frame_queue.put_nowait(display_frame)
                except:
                    pass  # 队列满，丢弃旧帧

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
                logger.warning(f"摄像头 {self.camera_id} 没有配置检测区域")
                return  # 没有配置检测区域，跳过检测

            logger.info(f"摄像头 {self.camera_id} 有 {len(zones)} 个检测区域")

            # 执行检测
            detections = self.detector.detect(frame)
            logger.info(f"摄像头 {self.camera_id} 检测到 {len(detections)} 个目标, 帧大小={frame.shape[:2]}")

            # 保存最新检测结果
            self.latest_detections = detections

            # 统计违规数量
            violations_in_zone = 0

            # 处理每个区域
            for zone in zones:
                try:
                    zone_coords = self.roi_manager.parse_coordinates(zone.coordinates)
                    height, width = frame.shape[:2]
                    scaled_coords = self.roi_manager.scale_coordinates(
                        zone_coords, width, height
                    )
                    logger.info(f"区域 {zone.name}: 归一化坐标={zone_coords}, 像素坐标={scaled_coords}")

                    detections_in_zone = 0

                    # 检查每个检测是否在区域内
                    for idx, detection in enumerate(detections):
                        bbox = detection['bbox']
                        center_x = (bbox[0] + bbox[2]) / 2
                        center_y = (bbox[1] + bbox[3]) / 2
                        is_in_zone = self.roi_manager.is_bbox_in_zone(detection['bbox'], scaled_coords)

                        logger.info(f"  目标{idx+1}: bbox={bbox}, center=({center_x:.1f},{center_y:.1f}), in_zone={is_in_zone}, class={detection.get('class_name')}, violation={detection.get('is_violation')}")

                        if is_in_zone:
                            detections_in_zone += 1
                            # 在区域内，检查是否违规
                            if detection.get('is_violation', False):
                                violations_in_zone += 1
                                logger.info(f"检测到违规: 摄像头{self.camera_id}, 区域{zone.name}, 类别={detection.get('class_name')}")
                                # 记录违规
                                self.violation_recorder.record_violation(
                                    self.camera_id,
                                    zone.id,
                                    frame,
                                    detection
                                )

                                # 调用回调函数（异步函数需要在新的事件循环中运行）
                                if self.on_detection_callback:
                                    def run_callback():
                                        try:
                                            loop = asyncio.new_event_loop()
                                            asyncio.set_event_loop(loop)
                                            loop.run_until_complete(self.on_detection_callback({
                                                'camera_id': self.camera_id,
                                                'zone_id': zone.id,
                                                'zone_name': zone.name,
                                                'detection': detection,
                                                'timestamp': datetime.now()
                                            }))
                                            loop.close()
                                        except Exception as e:
                                            logger.error(f"执行回调函数失败: {e}")

                                    # 在新线程中运行回调，避免阻塞检测线程
                                    callback_thread = threading.Thread(target=run_callback, daemon=True)
                                    callback_thread.start()

                    logger.info(f"区域 {zone.name} 内有 {detections_in_zone} 个目标")
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

    def _draw_detections(self, frame, detections) -> np.ndarray:
        """在帧上绘制检测框和标签"""
        for detection in detections:
            bbox = detection['bbox']
            x1, y1, x2, y2 = [int(v) for v in bbox]

            # 根据是否违规选择颜色
            is_violation = detection.get('is_violation', False)
            color = (0, 0, 255) if is_violation else (0, 255, 0)  # 红色违规，绿色正常
            label = detection.get('class_name', 'unknown')
            confidence = detection.get('confidence', 0)

            # 绘制检测框
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # 绘制标签和置信度
            label_text = f"{label}: {confidence:.2f}"
            label_size, _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 10),
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(frame, label_text, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        return frame

    def get_latest_detections(self) -> list:
        """获取最新的检测结果"""
        return self.latest_detections

    def _draw_zone_boundaries(self, frame) -> np.ndarray:
        """在帧上绘制检测区域边界"""
        try:
            from management.database import SessionLocal, DetectionZone
            db = SessionLocal()

            try:
                zones = db.query(DetectionZone).filter(
                    DetectionZone.camera_id == self.camera_id,
                    DetectionZone.enabled == True
                ).all()
            finally:
                db.close()

            if zones:
                height, width = frame.shape[:2]
                for zone in zones:
                    zone_coords = self.roi_manager.parse_coordinates(zone.coordinates)
                    scaled_coords = self.roi_manager.scale_coordinates(
                        zone_coords, width, height
                    )
                    cv2.polylines(frame, [np.array(scaled_coords, dtype=np.int32)],
                                 True, (255, 255, 0), 2)
                    # 绘制区域名称
                    if scaled_coords:
                        cv2.putText(frame, zone.name,
                                   (int(scaled_coords[0][0]), int(scaled_coords[0][1]) - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

        except Exception as e:
            logger.error(f"绘制区域边界失败: {e}")

        return frame
