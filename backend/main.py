# backend/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
import logging
import asyncio
import cv2
from config import settings
from pathlib import Path
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

# 全局变量：检测器和管理器
detector = None
roi_manager = None
violation_recorder = None
stream_processors = {}  # {camera_id: StreamProcessor}

# 全局WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """广播消息到所有连接的客户端"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# 检测回调函数
async def on_detection_callback(data: dict):
    """检测回调函数 - 当检测到违规时调用"""
    logger.info(f"检测到违规: 摄像头{data['camera_id']}, 区域{data['zone_id']}")

    # 广播到所有WebSocket连接
    await manager.broadcast({
        "type": "violation",
        "data": data
    })

# 应用启动和关闭事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    global detector, roi_manager, violation_recorder

    # 启动时执行
    logger.info("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成")

    # 初始化检测系统模块
    logger.info("初始化PPE检测器...")
    from detection import PPEDetector, ROIManager, ViolationRecorder

    detector = PPEDetector()
    roi_manager = ROIManager()
    violation_recorder = ViolationRecorder(str(settings.UPLOAD_DIR))

    logger.info("PPE检测系统初始化完成")
    logger.info("应用启动完成")
    yield

    # 关闭时执行
    logger.info("停止所有视频流处理器...")
    for processor in stream_processors.values():
        processor.stop()
    stream_processors.clear()
    logger.info("应用关闭")

# 创建FastAPI应用
app = FastAPI(
    title="制丝车间工装智能检测系统",
    description="广西中烟南宁卷烟厂制丝车间PPE（个人防护装备）智能检测系统API",
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

# ==================== 视频流处理API ====================

@app.post("/api/detection/start/{camera_id}")
async def start_detection(camera_id: int, background_tasks: BackgroundTasks):
    """启动指定摄像头的检测"""
    global detector, roi_manager, violation_recorder, stream_processors

    if camera_id in stream_processors:
        return {"status": "already_running", "message": f"摄像头 {camera_id} 已在运行中"}

    # 获取摄像头配置
    from management.database import SessionLocal, Camera
    db = SessionLocal()
    try:
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if not camera:
            return {"status": "error", "message": "摄像头不存在"}
    finally:
        db.close()

    # 创建视频流处理器
    from detection import StreamProcessor
    processor = StreamProcessor(
        source_url=camera.source_url,
        camera_id=camera_id,
        detector=detector,
        roi_manager=roi_manager,
        violation_recorder=violation_recorder,
        on_detection_callback=on_detection_callback
    )

    stream_processors[camera_id] = processor
    processor.start()

    return {"status": "started", "message": f"摄像头 {camera_id} 检测已启动"}

@app.post("/api/detection/stop/{camera_id}")
async def stop_detection(camera_id: int):
    """停止指定摄像头的检测"""
    global stream_processors

    if camera_id not in stream_processors:
        return {"status": "not_running", "message": f"摄像头 {camera_id} 未在运行中"}

    processor = stream_processors[camera_id]
    processor.stop()
    del stream_processors[camera_id]

    return {"status": "stopped", "message": f"摄像头 {camera_id} 检测已停止"}

@app.get("/api/detection/status")
async def get_detection_status():
    """获取所有摄像头的检测状态"""
    global stream_processors

    statuses = []
    for camera_id, processor in stream_processors.items():
        statuses.append(processor.get_status())

    return {
        "total": len(stream_processors),
        "processors": statuses
    }

@app.get("/api/detection/stream/{camera_id}")
async def get_stream_frame(camera_id: int):
    """获取指定摄像头的实时视频流帧（MJPEG格式）"""
    global stream_processors

    if camera_id not in stream_processors:
        return JSONResponse(
            status_code=404,
            content={"detail": f"摄像头 {camera_id} 未启动"}
        )

    processor = stream_processors[camera_id]

    def generate_frames():
        while True:
            frame = processor.get_latest_frame()
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                # 没有新帧，等待
                await asyncio.sleep(0.1)

    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "ppe-detection-system",
        "version": "1.0.0",
        "model": "PPE Detection (no_ppe/with_ppe)",
        "active_processors": len(stream_processors)
    }

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "制丝车间工装智能检测系统API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "detection": {
            "start": "POST /api/detection/start/{camera_id}",
            "stop": "POST /api/detection/stop/{camera_id}",
            "status": "GET /api/detection/status",
            "stream": "GET /api/detection/stream/{camera_id}"
        }
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
