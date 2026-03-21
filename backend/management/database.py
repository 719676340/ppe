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
