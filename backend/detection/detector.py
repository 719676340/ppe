# backend/detection/detector.py
from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Dict, Tuple
from config import settings
from pathlib import Path
import os
os.environ['PYTHONWARNINGS'] = 'ignore'

# 解决 PyTorch 2.6 weights_only=True 的问题
# Monkey patch torch.load to use weights_only=False for YOLO models
import torch
_original_torch_load = torch.load

def _patched_torch_load(f, *args, **kwargs):
    """临时修复 torch.load 以支持 YOLO 模型加载"""
    # 如果没有设置 weights_only，默认设为 False
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_torch_load(f, *args, **kwargs)

torch.load = _patched_torch_load

class PPEDetector:
    """PPE（个人防护装备）检测器 - 使用训练好的YOLO模型

    模型类别：
    - 0: no_ppe - 未佩戴PPE/未穿工服（需要告警）
    - 1: with_ppe - 佩戴PPE/穿工服（正常）
    """

    def __init__(self, model_path: Path = None):
        """初始化检测器"""
        model_path = model_path or settings.YOLO_MODEL_PATH
        try:
            self.model = YOLO(str(model_path))
            self.class_names = self.model.names
            print(f"模型加载成功，类别: {self.class_names}")
        except Exception as e:
            raise RuntimeError(f"无法加载YOLO模型: {e}")

        # 检测参数
        self.confidence_threshold = settings.DEFAULT_CONFIDENCE_THRESHOLD
        self.iou_threshold = settings.DEFAULT_IOU_THRESHOLD
        self.violation_class_id = settings.VIOLATION_CLASS_ID

    def detect(self, image: np.ndarray) -> List[Dict]:
        """
        检测图像中的PPE佩戴情况

        Args:
            image: OpenCV图像 (BGR格式)

        Returns:
            检测结果列表，每个元素包含:
            {
                'bbox': [x1, y1, x2, y2],  # 边界框坐标
                'confidence': float,        # 置信度
                'class_id': int,           # 类别ID
                'class_name': str,         # 类别名称
                'is_compliant': bool       # 是否符合规范（已佩戴PPE）
            }
        """
        import logging
        logger = logging.getLogger(__name__)

        results = self.model(
            image,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            verbose=False
        )

        detections = []
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            logger.info(f"[DETECTOR] 检测到 {len(boxes)} 个目标，违规类别ID={self.violation_class_id}")
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())

                # 判断是否符合规范（已佩戴PPE）
                # class_id == 1 表示 with_ppe（正常）
                is_compliant = class_id == 1
                is_violation = class_id == self.violation_class_id

                detection = {
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'confidence': confidence,
                    'class_id': class_id,
                    'class_name': self.class_names[class_id],
                    'is_compliant': is_compliant,
                    'is_violation': is_violation
                }

                detections.append(detection)
                logger.info(f"[DETECTOR] 目标: class_id={class_id}, class_name={self.class_names[class_id]}, is_violation={is_violation}, confidence={confidence:.2f}")
        else:
            logger.info(f"[DETECTOR] 未检测到任何目标")

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
