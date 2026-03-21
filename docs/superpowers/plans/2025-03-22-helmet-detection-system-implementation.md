# 制丝车间安全头盔智能检测系统 - 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个完整的安全头盔智能检测系统，包含RTSP视频流接入、YOLO 11M模型检测、ROI区域配置、违规记录管理和统计分析功能。

**Architecture:** 单体应用架构，Python FastAPI后端 + Vue 3前端 + SQLite数据库，内部分为检测系统模块和信息管理模块两个独立部分用于软著申请。

**Tech Stack:**
- 后端: Python 3.10+, FastAPI, SQLAlchemy, ultralytics YOLO 11M, OpenCV
- 前端: Vue 3, Element Plus, ECharts, Pinia
- 数据库: SQLite
- 视频处理: OpenCV, FFmpeg

---

## 项目结构概览

```
helmet_detection/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── detection/                    # 检测系统模块 (软著一)
│   │   ├── __init__.py
│   │   ├── detector.py
│   │   ├── stream_processor.py
│   │   ├── roi_manager.py
│   │   └── violation_recorder.py
│   ├── management/                   # 信息管理模块 (软著二)
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── routers/
│   │   └── exporters/
│   ├── models/
│   │   └── yolo11m.pt
│   └── static/uploads/
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── views/
│   │   ├── components/
│   │   ├── api/
│   │   └── stores/
│   ├── package.json
│   └── vite.config.js
└── docs/
```

---

## Task 1: 项目初始化

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/config.py`
- Create: `frontend/package.json`
- Create: `README.md`

- [ ] **Step 1: 创建后端依赖文件**

```txt
# backend/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-multipart==0.0.6
ultralytics==8.0.206
opencv-python==4.8.1.78
numpy==1.24.3
pillow==10.1.0
websockets==12.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
openpyxl==3.1.2
reportlab==4.0.7
aiofiles==23.2.1
```

- [ ] **Step 2: 创建后端配置文件**

```python
# backend/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./database.db"

    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # 文件存储配置
    UPLOAD_DIR: str = "./static/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 检测配置
    YOLO_MODEL_PATH: str = "./models/yolo11m.pt"
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.5
    DEFAULT_IOU_THRESHOLD: float = 0.45
    DEFAULT_DEDUP_INTERVAL: int = 300  # 秒

    # 视频流配置
    RTSP_RECONNECT_INTERVAL: int = 10  # 秒
    MAX_RECONNECT_ATTEMPTS: int = 5

    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 3: 创建前端配置文件**

```json
{
  "name": "helmet-detection-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.3.8",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "element-plus": "^2.4.4",
    "echarts": "^5.4.3",
    "axios": "^1.6.2",
    "@element-plus/icons-vue": "^2.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.5.0",
    "vite": "^5.0.2"
  }
}
```

- [ ] **Step 4: 创建Vite配置**

```javascript
// frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true
      }
    }
  }
})
```

- [ ] **Step 5: 创建README文档**

```markdown
# 制丝车间安全头盔智能检测系统

广西中烟南宁卷烟厂制丝车间安全头盔智能检测系统。

## 快速开始

### 后端启动
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 技术栈
- 后端: FastAPI + YOLO 11M + OpenCV
- 前端: Vue 3 + Element Plus + ECharts
- 数据库: SQLite
```

---

## Task 2: 数据库初始化

**Files:**
- Create: `backend/management/database.py`
- Create: `backend/init_db.py`

- [ ] **Step 1: 创建数据库模型**

```python
# backend/management/database.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, ForeignKey, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    source_type = Column(String(20), nullable=False)  # 'rtsp'/'file'/'usb'
    source_url = Column(String(500))
    location = Column(String(100))
    status = Column(String(20), default="active")  # 'active'/'inactive'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    zones = relationship("DetectionZone", back_populates="camera", cascade="all, delete-orphan")

class DetectionZone(Base):
    __tablename__ = "detection_zones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    name = Column(String(100), nullable=False)
    coordinates = Column(Text, nullable=False)  # JSON格式
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    camera = relationship("Camera", back_populates="zones")

class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("detection_zones.id"))
    violation_time = Column(DateTime, nullable=False)
    image_path = Column(String(500))
    is_processed = Column(Boolean, default=False)
    remark = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)  # 'violation'/'warning'/'info'/'success'
    title = Column(String(200), nullable=False)
    message = Column(Text)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    zone_id = Column(Integer, ForeignKey("detection_zones.id"))
    violation_id = Column(Integer, ForeignKey("violations.id"))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text)
    description = Column(String(200))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="operator")  # 'admin'/'operator'
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 2: 创建数据库初始化脚本**

```python
# backend/init_db.py
from management.database import engine, Base, SystemConfig
from datetime import datetime

def init_db():
    """初始化数据库表和默认配置"""
    Base.metadata.create_all(bind=engine)

    # 插入默认检测参数配置
    default_configs = [
        {"config_key": "detection.confidence_threshold", "config_value": "0.5", "description": "检测置信度阈值"},
        {"config_key": "detection.iou_threshold", "config_value": "0.45", "description": "NMS IOU阈值"},
        {"config_key": "detection.dedup_interval", "config_value": "300", "description": "违规去重时间间隔（秒）"},
        {"config_key": "detection.max_distance", "config_value": "200", "description": "检测最大距离（像素）"},
    ]

    from management.database import SessionLocal
    db = SessionLocal()
    try:
        for config in default_configs:
            existing = db.query(SystemConfig).filter(SystemConfig.config_key == config["config_key"]).first()
            if not existing:
                db_config = SystemConfig(**config)
                db.add(db_config)
        db.commit()
        print("数据库初始化成功！")
    except Exception as e:
        db.rollback()
        print(f"数据库初始化失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
```

- [ ] **Step 3: 运行数据库初始化**

```bash
cd backend
python init_db.py
```

Expected: 数据库文件 `backend/database.db` 被创建

---

## Task 3: 检测系统模块 - YOLO检测器

**Files:**
- Create: `backend/detection/__init__.py`
- Create: `backend/detection/detector.py`

- [ ] **Step 1: 创建检测器模块**

```python
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
```

- [ ] **Step 2: 创建模块初始化文件**

```python
# backend/detection/__init__.py
from .detector import HelmetDetector
from .stream_processor import StreamProcessor
from .roi_manager import ROIManager
from .violation_recorder import ViolationRecorder

__all__ = ['HelmetDetector', 'StreamProcessor', 'ROIManager', 'ViolationRecorder']
```

---

## Task 4: 检测系统模块 - ROI区域管理

**Files:**
- Create: `backend/detection/roi_manager.py`

- [ ] **Step 1: 创建ROI管理器**

```python
# backend/detection/roi_manager.py
import json
import cv2
import numpy as np
from typing import List, Dict, Tuple

class ROIManager:
    """ROI (感兴趣区域) 管理器"""

    @staticmethod
    def parse_coordinates(coordinates_json: str) -> List[Tuple[float, float]]:
        """
        解析ROI坐标字符串

        Args:
            coordinates_json: JSON格式的坐标字符串

        Returns:
            归一化坐标列表 [(x1, y1), (x2, y2), ...]
        """
        try:
            coords = json.loads(coordinates_json)
            return [(float(x), float(y)) for x, y in coords]
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            raise ValueError(f"无效的坐标格式: {e}")

    @staticmethod
    def scale_coordinates(
        normalized_coords: List[Tuple[float, float]],
        image_width: int,
        image_height: int
    ) -> List[Tuple[int, int]]:
        """
        将归一化坐标转换为实际像素坐标

        Args:
            normalized_coords: 归一化坐标 [(x1, y1), ...]
            image_width: 图像宽度
            image_height: 图像高度

        Returns:
            实际像素坐标 [(x1, y1), ...]
        """
        return [
            (int(x * image_width), int(y * image_height))
            for x, y in normalized_coords
        ]

    @staticmethod
    def point_in_polygon(
        point: Tuple[float, float],
        polygon: List[Tuple[float, float]]
    ) -> bool:
        """
        判断点是否在多边形内 (射线法)

        Args:
            point: 待判断点 (x, y)
            polygon: 多边形顶点列表 [(x1, y1), (x2, y2), ...]

        Returns:
            True表示在多边形内，False表示在多边形外
        """
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def is_bbox_in_zone(
        self,
        bbox: List[float],
        zone_coords: List[Tuple[float, float]]
    ) -> bool:
        """
        判断边界框中心点是否在检测区域内

        Args:
            bbox: 边界框 [x1, y1, x2, y2]
            zone_coords: 区域顶点坐标列表 [(x1, y1), ...]

        Returns:
            True表示在区域内，False表示在区域外
        """
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2
        return self.point_in_polygon((center_x, center_y), zone_coords)

    def draw_zone(
        self,
        image: np.ndarray,
        zone_coords: List[Tuple[int, int]],
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2
    ) -> np.ndarray:
        """
        在图像上绘制检测区域

        Args:
            image: OpenCV图像
            zone_coords: 区域顶点坐标列表
            color: 颜色 (B, G, R)
            thickness: 线条粗细

        Returns:
            绘制后的图像
        """
        image_copy = image.copy()
        if len(zone_coords) >= 3:
            pts = np.array(zone_coords, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(image_copy, [pts], True, color, thickness)
        return image_copy
```

---

## Task 5: 检测系统模块 - 视频流处理器

**Files:**
- Create: `backend/detection/stream_processor.py`

- [ ] **Step 1: 创建视频流处理器**

```python
# backend/detection/stream_processor.py
import cv2
import threading
import time
from queue import Queue
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StreamProcessor:
    """RTSP视频流处理器"""

    def __init__(
        self,
        source_url: str,
        camera_id: int,
        detector,
        roi_manager,
        violation_recorder
    ):
        """
        初始化视频流处理器

        Args:
            source_url: RTSP流地址或本地文件路径
            camera_id: 摄像头ID
            detector: 检测器实例
            roi_manager: ROI管理器实例
            violation_recorder: 违规记录器实例
        """
        self.source_url = source_url
        self.camera_id = camera_id
        self.detector = detector
        self.roi_manager = roi_manager
        self.violation_recorder = violation_recorder

        self.running = False
        self.thread = None
        self.cap = None
        self.frame_queue = Queue(maxsize=30)  # 保存最近30帧

        # 断线检测
        self.last_frame_time = None
        self.is_online = True
        self.reconnect_attempts = 0

    def start(self):
        """启动视频流处理"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._process_stream, daemon=True)
        self.thread.start()
        logger.info(f"摄像头 {self.camera_id} 视频流处理已启动")

    def stop(self):
        """停止视频流处理"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        if self.cap:
            self.cap.release()
        logger.info(f"摄像头 {self.camera_id} 视频流处理已停止")

    def _connect_stream(self) -> Optional[cv2.VideoCapture]:
        """连接视频流"""
        try:
            cap = cv2.VideoCapture(self.source_url)
            if not cap.isOpened():
                logger.error(f"无法连接到视频流: {self.source_url}")
                return None

            # 设置缓冲区大小
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            return cap
        except Exception as e:
            logger.error(f"连接视频流时出错: {e}")
            return None

    def _process_stream(self):
        """处理视频流的主循环"""
        while self.running:
            if self.cap is None:
                self.cap = self._connect_stream()
                if self.cap is None:
                    self._handle_disconnect()
                    time.sleep(5)  # 等待后重试
                    continue

            ret, frame = self.cap.read()
            if not ret:
                self._handle_disconnect()
                self.cap.release()
                self.cap = None
                time.sleep(2)
                continue

            # 连接成功
            if not self.is_online:
                self._handle_reconnect()

            self.last_frame_time = datetime.now()

            # 将帧放入队列
            if not self.frame_queue.full():
                self.frame_queue.put(frame)

            # 执行检测
            self._detect_frame(frame)

            # 控制帧率
            time.sleep(0.033)  # 约30fps

    def _detect_frame(self, frame):
        """对单帧进行检测"""
        try:
            # 获取该摄像头的所有区域
            from management.database import SessionLocal, DetectionZone
            db = SessionLocal()
            zones = db.query(DetectionZone).filter(
                DetectionZone.camera_id == self.camera_id,
                DetectionZone.enabled == True
            ).all()
            db.close()

            if not zones:
                return

            # 执行检测
            detections = self.detector.detect(frame)

            # 处理每个区域
            for zone in zones:
                zone_coords = self.roi_manager.parse_coordinates(zone.coordinates)
                height, width = frame.shape[:2]
                scaled_coords = self.roi_manager.scale_coordinates(
                    zone_coords, width, height
                )

                # 检查每个检测是否在区域内
                for detection in detections:
                    if self.roi_manager.is_bbox_in_zone(detection['bbox'], scaled_coords):
                        # 在区域内，检查是否佩戴头盔
                        if not detection['has_helmet']:
                            # 未佩戴头盔，记录违规
                            self.violation_recorder.record_violation(
                                self.camera_id,
                                zone.id,
                                frame,
                                detection
                            )

        except Exception as e:
            logger.error(f"检测帧时出错: {e}")

    def _handle_disconnect(self):
        """处理断线"""
        if self.is_online:
            self.is_online = False
            self.reconnect_attempts += 1
            logger.warning(f"摄像头 {self.camera_id} 断线，尝试重连...")

            # TODO: 发送断线通知
            # from management.services.notification_service import create_notification
            # create_notification(...)

    def _handle_reconnect(self):
        """处理重连成功"""
        self.is_online = True
        self.reconnect_attempts = 0
        logger.info(f"摄像头 {self.camera_id} 重连成功")

    def get_latest_frame(self) -> Optional[Any]:
        """获取最新帧"""
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return None

    def get_status(self) -> Dict[str, Any]:
        """获取处理器状态"""
        return {
            "camera_id": self.camera_id,
            "is_online": self.is_online,
            "is_running": self.running,
            "reconnect_attempts": self.reconnect_attempts,
            "last_frame_time": self.last_frame_time
        }
```

---

## Task 6: 检测系统模块 - 违规记录器

**Files:**
- Create: `backend/detection/violation_recorder.py`

- [ ] **Step 1: 创建违规记录器**

```python
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
```

---

## Task 7: 信息管理模块 - Pydantic模型

**Files:**
- Create: `backend/management/schemas/__init__.py`
- Create: `backend/management/schemas/camera.py`
- Create: `backend/management/schemas/zone.py`
- Create: `backend/management/schemas/violation.py`
- Create: `backend/management/schemas/statistics.py`
- Create: `backend/management/schemas/notification.py`

- [ ] **Step 1: 创建摄像头数据模型**

```python
# backend/management/schemas/camera.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CameraBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    source_type: str = Field(..., pattern="^(rtsp|file|usb)$")
    source_url: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    status: str = Field("active", pattern="^(active|inactive)$")

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    source_type: Optional[str] = Field(None, pattern="^(rtsp|file|usb)$")
    source_url: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")

class CameraResponse(CameraBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CameraTestRequest(BaseModel):
    source_type: str = Field(..., pattern="^(rtsp|file|usb)$")
    source_url: str

class CameraTestResponse(BaseModel):
    success: bool
    message: str
    resolution: Optional[str] = None
    fps: Optional[float] = None
```

- [ ] **Step 2: 创建区域数据模型**

```python
# backend/management/schemas/zone.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DetectionZoneBase(BaseModel):
    camera_id: int
    name: str = Field(..., min_length=1, max_length=100)
    coordinates: str  # JSON格式: [[x1,y1],[x2,y2],...]
    enabled: bool = True

class DetectionZoneCreate(DetectionZoneBase):
    pass

class DetectionZoneUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    coordinates: Optional[str] = None
    enabled: Optional[bool] = None

class DetectionZoneResponse(DetectionZoneBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **Step 3: 创建违规记录数据模型**

```python
# backend/management/schemas/violation.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ViolationBase(BaseModel):
    camera_id: int
    zone_id: Optional[int] = None
    violation_time: datetime
    image_path: Optional[str] = None
    is_processed: bool = False
    remark: Optional[str] = None

class ViolationResponse(ViolationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ViolationListResponse(BaseModel):
    total: int
    items: list[ViolationResponse]

class ViolationFilter(BaseModel):
    camera_id: Optional[int] = None
    zone_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_processed: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
```

- [ ] **Step 4: 创建统计数据模型**

```python
# backend/management/schemas/statistics.py
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class ZoneStatisticsResponse(BaseModel):
    zone_id: int
    zone_name: str
    camera_id: int
    camera_name: str
    violation_count: int

class PeriodStatisticsResponse(BaseModel):
    period: str  # 'morning'/'afternoon'/'night'
    violation_count: int

class CameraStatisticsResponse(BaseModel):
    camera_id: int
    camera_name: str
    violation_count: int

class TrendDataPoint(BaseModel):
    date: str
    count: int

class TrendStatisticsResponse(BaseModel):
    data: List[TrendDataPoint]
```

- [ ] **Step 5: 创建通知数据模型**

```python
# backend/management/schemas/notification.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    type: str = Field(..., pattern="^(violation|warning|info|success)$")
    title: str = Field(..., min_length=1, max_length=200)
    message: Optional[str] = None
    camera_id: Optional[int] = None
    zone_id: Optional[int] = None
    violation_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    total: int
    unread_count: int
    items: list[NotificationResponse]
```

---

## Task 8: 信息管理模块 - 服务层

**Files:**
- Create: `backend/management/services/__init__.py`
- Create: `backend/management/services/camera_service.py`
- Create: `backend/management/services/zone_service.py`
- Create: `backend/management/services/violation_service.py`
- Create: `backend/management/services/statistics_service.py`
- Create: `backend/management/services/notification_service.py`

- [ ] **Step 1: 创建摄像头服务**

```python
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
```

继续服务层的其他文件...

---

## 实施说明

由于篇幅限制，以上是核心模块的详细实施步骤。后续需要完成：

1. **后端API路由** - 实现所有RESTful API端点
2. **WebSocket服务** - 实时推送检测结果
3. **前端页面** - Vue组件和页面
4. **前端API调用** - Axios封装
5. **前端状态管理** - Pinia stores

每个任务应遵循TDD原则，先写测试再实现功能，每完成一个功能点就提交代码。
