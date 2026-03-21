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
