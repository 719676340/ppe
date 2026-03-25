# backend/config.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings
import secrets

# 获取项目根目录（backend目录的父目录）
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # 数据库配置 - 使用绝对路径
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/database.db"

    # JWT配置 - 生产环境必须设置SECRET_KEY
    SECRET_KEY: str = secrets.token_urlsafe(32) if os.getenv("ENVIRONMENT") != "production" else ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # 文件存储配置 - 使用绝对路径并确保目录存在
    UPLOAD_DIR: Path = BASE_DIR / "static" / "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 检测配置
    YOLO_MODEL_PATH: Path = BASE_DIR / "models" / "train" / "weights" / "best.pt"
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.5
    DEFAULT_IOU_THRESHOLD: float = 0.45
    DEFAULT_DEDUP_INTERVAL: int = 30  # 秒（去重时间间隔）
    DEFAULT_DEDUP_DISTANCE: int = 100  # 像素（判定为同一位置的最大距离）
    AUTO_START_DETECTION: bool = True  # 应用启动时自动启动已启用的摄像头检测

    # 模型类别配置 (根据训练模型调整)
    # 0: no_ppe - 未佩戴PPE/未穿工服（需要告警）- 违规
    # 1: with_ppe - 佩戴PPE/穿工服（正常）
    VIOLATION_CLASS_ID: int = 0  # 不戴安全帽的才是违规

    # 视频流配置
    DEFAULT_STREAM_URL: str = "rtmp://localhost/mystream"  # 默认视频流地址
    RTSP_RECONNECT_INTERVAL: int = 10  # 秒
    MAX_RECONNECT_ATTEMPTS: int = 5

    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保上传目录存在
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    class Config:
        env_file = ".env"

settings = Settings()
