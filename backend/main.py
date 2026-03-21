# backend/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from config import settings
from management.database import engine, Base
from management.routers import (
    camera_router, zone_router, violation_router,
    statistics_router, notification_router
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# 应用启动和关闭事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    logger.info("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成")

    # TODO: 初始化检测器和视频流处理器
    # from detection import HelmetDetector, StreamProcessor, ROIManager, ViolationRecorder
    # detector = HelmetDetector()
    # roi_manager = ROIManager()
    # violation_recorder = ViolationRecorder()

    logger.info("应用启动完成")
    yield

    # 关闭时执行
    logger.info("应用关闭")

# 创建FastAPI应用
app = FastAPI(
    title="制丝车间安全头盔智能检测系统",
    description="广西中烟南宁卷烟厂制丝车间安全头盔智能检测系统API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="./static"), name="static")

# 注册路由
app.include_router(camera_router)
app.include_router(zone_router)
app.include_router(violation_router)
app.include_router(statistics_router)
app.include_router(notification_router)

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "helmet-detection-system",
        "version": "1.0.0"
    }

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "制丝车间安全头盔智能检测系统API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# WebSocket端点 - 实时检测结果推送
@app.websocket("/ws/detection")
async def detection_websocket(websocket: WebSocket):
    """WebSocket端点 - 接收实时检测结果"""
    await manager.connect(websocket)
    try:
        while True:
            # 接收客户端消息（例如心跳）
            data = await websocket.receive_text()

            # 这里可以处理客户端发送的消息
            # 例如：开始/停止检测、切换摄像头等

            # 发送确认
            await websocket.send_json({"type": "ping", "status": "connected"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket客户端断开连接")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        manager.disconnect(websocket)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"全局异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
