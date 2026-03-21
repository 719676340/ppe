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
