# backend/detection/detector.py
from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Dict, Tuple
from config import settings

class HelmetDetector:
    """头盔检测器 - 使用YOLO 11M模型"""

    def __init__(self, model_path: str = None):
        """初始化检测器"""
        model_path = model_path or settings.YOLO_MODEL_PATH
        try:
            self.model = YOLO(model_path)
            self.class_names = self.model.names
        except Exception as e:
            raise RuntimeError(f"无法加载YOLO模型: {e}")

        # 检测参数
        self.confidence_threshold = settings.DEFAULT_CONFIDENCE_THRESHOLD
        self.iou_threshold = settings.DEFAULT_IOU_THRESHOLD

    def detect(self, image: np.ndarray) -> List[Dict]:
        """
        检测图像中的人员和头盔

        Args:
            image: OpenCV图像 (BGR格式)

        Returns:
            检测结果列表，每个元素包含:
            {
                'bbox': [x1, y1, x2, y2],  # 边界框坐标
                'confidence': float,        # 置信度
                'class_id': int,           # 类别ID (0=人, 1=佩戴头盔, 2=未佩戴头盔)
                'class_name': str,         # 类别名称
                'has_helmet': bool         # 是否佩戴头盔
            }
        """
        results = self.model(
            image,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            verbose=False
        )

        detections = []
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())

                # 判断是否佩戴头盔
                # 假设类别: 0=person, 1=person_with_helmet, 2=person_without_helmet
                has_helmet = class_id == 1

                detections.append({
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'confidence': confidence,
                    'class_id': class_id,
                    'class_name': self.class_names[class_id],
                    'has_helmet': has_helmet
                })

        return detections

    def set_confidence_threshold(self, threshold: float):
        """设置置信度阈值"""
        self.confidence_threshold = max(0.1, min(1.0, threshold))

    def set_iou_threshold(self, threshold: float):
        """设置IOU阈值"""
        self.iou_threshold = max(0.1, min(1.0, threshold))

    def get_center_point(self, bbox: List[float]) -> Tuple[float, float]:
        """获取边界框中心点"""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
