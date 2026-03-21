# 制丝车间安全头盔智能检测系统 - 设计文档

## 项目概述

为广西中烟南宁卷烟厂制丝车间开发一套安全头盔智能检测系统，通过接入RTSP视频流，使用YOLO 11M模型检测特定区域内人员是否佩戴头盔，未佩戴则记录并截图。系统包含两个独立部分用于软著申请。

## 软著划分

1. **《制丝车间安全头盔智能检测系统》** - detection/ 目录代码
2. **《制丝车间安全管理信息系统》** - management/ 目录代码

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         前端 (Vue 3 + Element Plus)                      │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐ │
│  │           检测演示模块            │  │        信息管理模块           │ │
│  │  ┌────────────────────────────┐  │  │  ┌────────────────────────┐ │ │
│  │  │  实时监控看板              │  │  │  │  违规记录管理          │ │ │
│  │  │  - 多路视频分屏展示        │  │  │  │  - 记录列表/详情       │ │ │
│  │  │  - 检测结果实时叠加        │  │  │  │  - 图片预览/播放       │ │ │
│  │  │  - 违规闪烁报警            │  │  │  │  - 按条件筛选查询      │ │ │
│  │  │  - 断线状态告警            │  │  │  │  - 批量删除/导出      │ │ │
│  │  │  - 实时统计数据            │  │  │  └────────────────────────┘ │ │
│  │  └────────────────────────────┘  │  │  ┌────────────────────────┐ │ │
│  │  ┌────────────────────────────┐  │  │  │  统计分析中心          │ │ │
│  │  │  ROI配置工具              │  │  │  │  - 区域违规对比图      │ │ │
│  │  │  - 视频画面加载            │  │  │  │  - 时段违规分析        │ │ │
│  │  │  - 多边形区域绘制          │  │  │  │  - 摄像头违规统计      │ │ │
│  │  │  - 区域编辑/删除           │  │  │  │  - 违规趋势图          │ │ │
│  │  │  - 区域名称设置            │  │  │  └────────────────────────┘ │ │
│  │  └────────────────────────────┘  │  │  ┌────────────────────────┐ │ │
│  └──────────────────────────────────┘  │  │  系统配置中心          │ │ │
│                                        │  │  - 摄像头管理          │ │ │
│  ┌──────────────────────────────────┐  │  │  - 检测参数配置        │ │ │
│  │  系统通知中心                    │  │  │  - 置信度阈值设置      │ │ │
│  │  - 实时通知消息                  │  │  └────────────────────────┘ │ │
│  │  - 通知历史记录                  │  │                              │ │
│  └──────────────────────────────────┘  └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      后端 (FastAPI)                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  ┌─────────────────────────────┐│
│  │       检测系统模块 (软著一)         │  │    信息管理模块 (软著二)      ││
│  │  - RTSP视频流接入                  │  │  - 违规记录 CRUD             ││
│  │  - YOLO 11M模型推理                │  │  - 统计分析 API              ││
│  │  - ROI区域检测                     │  │  - 摄像头/区域配置           ││
│  │  - 违规截图保存                    │  │  - 数据导出                  ││
│  │  - WebSocket实时推送               │  │  - 用户认证                  ││
│  │  - 断线监控与告警                  │  │  - 通知消息管理              ││
│  │  - 检测参数管理                    │  │  - 系统配置管理              ││
│  └───────────────────────────────────┘  └─────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SQLite 数据库                                         │
│  violations | cameras | detection_zones | system_config | users         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 核心业务流程

### 1. 系统启动流程
```
加载配置 → 初始化YOLO模型 → 连接视频流 → 启动检测线程 → 启动WebSocket服务
```

### 2. 检测流程
```
读取视频帧 → YOLO推理 → 过滤ROI区域 → 头盔判断
    → [未佩戴] → 截图 → 生成记录 → 存库 → 推送前端 → 触发报警
    → [已佩戴] → 更新统计 → 推送正常状态
```

### 3. 违规去重机制
同一人员同一区域，5分钟内只记录一次，避免重复报警（可配置间隔时间）

### 4. 摄像头配置流程
```
系统配置中心 → 摄像头管理 → 添加摄像头
    → 输入名称/RTSP地址/位置 → 测试连接 → 保存
```

### 5. ROI区域配置流程
```
ROI配置工具 → 选择摄像头 → 加载画面
    → 绘制多边形区域 → 设置区域名称 → 预览 → 保存
```

### 6. 数据导出流程
```
选择时间范围 → 选择摄像头/区域 → 生成预览
    → 选择导出格式 → Excel/PDF/ZIP → 下载
```

### 7. RTSP断线处理流程
```
读取视频帧 → 连续失败3次 → 标记为断线
    → 停止检测线程 → 推送断线告警 → 前端显示告警
    → 后台尝试重连（每10秒） → 重连成功 → 恢复检测
```

### 8. 系统通知流程
```
检测事件 → 生成通知消息 → 存入通知表
    → WebSocket推送前端 → 前端通知中心显示 → 用户查看标记已读
```

## 检测参数配置

系统支持在Web界面配置以下检测参数：

| 参数 | 说明 | 默认值 | 范围 |
|------|------|--------|------|
| confidence_threshold | 检测置信度阈值 | 0.5 | 0.1-1.0 |
| iou_threshold | NMS IOU阈值 | 0.45 | 0.1-1.0 |
| dedup_interval | 违规去重时间间隔（秒） | 300 | 0-3600 |
| max_detection_distance | 检测最大距离（像素） | 200 | 50-500 |

## 数据库设计

```sql
-- 摄像头表
CREATE TABLE cameras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    source_type VARCHAR(20) NOT NULL,  -- 'rtsp'/'file'/'usb'
    source_url VARCHAR(500),
    location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',  -- 'active'/'inactive'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 区域配置表
CREATE TABLE detection_zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    coordinates TEXT NOT NULL,  -- JSON格式的多边形顶点坐标
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE
);

-- 违规记录表
CREATE TABLE violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER NOT NULL,
    zone_id INTEGER,
    violation_time TIMESTAMP NOT NULL,
    image_path VARCHAR(500),
    is_processed BOOLEAN DEFAULT 0,
    remark TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(id),
    FOREIGN KEY (zone_id) REFERENCES detection_zones(id) ON DELETE SET NULL
);

-- 系统配置表
CREATE TABLE system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description VARCHAR(200)
);

-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'operator',  -- 'admin'/'operator'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 通知消息表
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type VARCHAR(50) NOT NULL,  -- 'violation'/'warning'/'info'/'success'
    title VARCHAR(200) NOT NULL,
    message TEXT,
    camera_id INTEGER,
    zone_id INTEGER,
    violation_id INTEGER,
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE SET NULL,
    FOREIGN KEY (zone_id) REFERENCES detection_zones(id) ON DELETE SET NULL,
    FOREIGN KEY (violation_id) REFERENCES violations(id) ON DELETE SET NULL
);

-- 系统配置表（补充检测参数配置）
INSERT INTO system_config (config_key, config_value, description) VALUES
    ('detection.confidence_threshold', '0.5', '检测置信度阈值'),
    ('detection.iou_threshold', '0.45', 'NMS IOU阈值'),
    ('detection.dedup_interval', '300', '违规去重时间间隔（秒）'),
    ('detection.max_distance', '200', '检测最大距离（像素）');

-- 创建索引
CREATE INDEX idx_violations_time ON violations(violation_time);
CREATE INDEX idx_violations_camera ON violations(camera_id);
CREATE INDEX idx_zones_camera ON detection_zones(camera_id);
```

## 前端页面结构

```
src/
├── main.js
├── App.vue
├── router/
│   └── index.js                     # 路由配置
├── views/
│   ├── Detection/                    # 检测演示模块
│   │   ├── MonitorDashboard.vue      # 实时监控看板
│   │   │   ├── VideoPlayer.vue       # 视频播放器组件
│   │   │   ├── DetectionOverlay.vue  # 检测框叠加层
│   │   │   └── StatisticsPanel.vue   # 实时统计面板
│   │   └── ROIConfig.vue             # ROI配置工具
│   │       ├── VideoCanvas.vue       # 视频画布（支持绘制）
│   │       ├── ZoneEditor.vue        # 区域编辑器
│   │       └── ZoneList.vue          # 区域列表
│   └── Management/                   # 信息管理模块
│       ├── ViolationRecords.vue      # 违规记录管理
│       │   ├── RecordTable.vue       # 记录表格
│       │   ├── ImagePreview.vue      # 图片预览
│       │   └── FilterPanel.vue       # 筛选面板
│       ├── StatisticsCenter.vue      # 统计分析中心
│       │   ├── ZoneChart.vue         # 区域对比图
│       │   ├── TimeChart.vue         # 时段分析图
│       │   ├── CameraChart.vue       # 摄像头统计图
│       │   └── TrendChart.vue        # 趋势图
│       └── SystemConfig.vue          # 系统配置中心
│           ├── CameraManager.vue     # 摄像头管理
│           ├── DetectionConfig.vue   # 检测参数配置
│           └── DataManagement.vue    # 数据管理（备份/导出）
├── components/
│   ├── common/
│   │   └── ...
│   ├── NotificationCenter.vue        # 通知中心组件
│   ├── NotificationBadge.vue         # 通知角标
│   └── charts/                       # 图表组件
│       └── ...
└── api/
    ├── index.js                      # API实例配置
    ├── camera.js                     # 摄像头API
    ├── zone.js                       # 区域API
    ├── violation.js                  # 违规记录API
    └── statistics.js                 # 统计API
```

## 后端代码结构

```
helmet_detection/
├── main.py                           # FastAPI主入口
├── config.py                         # 配置文件
├── requirements.txt                  # Python依赖
├── detection/                        # 检测系统模块 (软著一)
│   ├── __init__.py
│   ├── detector.py                   # YOLO检测器
│   ├── stream_processor.py           # RTSP流处理器
│   ├── roi_manager.py                # ROI区域管理
│   └── violation_recorder.py         # 违规记录器
├── management/                       # 信息管理模块 (软著二)
│   ├── __init__.py
│   ├── database.py                   # 数据库连接和模型
│   ├── schemas/                      # Pydantic数据模型
│   │   ├── camera.py
│   │   ├── zone.py
│   │   ├── violation.py
│   │   ├── statistics.py
│   │   └── notification.py           # 通知数据模型
│   ├── services/
│   │   ├── camera_service.py         # 摄像头业务逻辑
│   │   ├── zone_service.py           # 区域业务逻辑
│   │   ├── violation_service.py      # 违规记录业务逻辑
│   │   ├── statistics_service.py     # 统计分析业务逻辑
│   │   └── notification_service.py   # 通知服务
│   ├── routers/
│   │   ├── camera.py                 # 摄像头API路由
│   │   ├── zone.py                   # 区域API路由
│   │   ├── violation.py              # 违规记录API路由
│   │   ├── statistics.py             # 统计API路由
│   │   └── notification.py           # 通知API路由
│   └── exporters/
│       ├── excel_exporter.py         # Excel导出
│       └── pdf_exporter.py           # PDF报告导出
├── models/
│   └── yolo11m.pt                    # YOLO 11M模型文件
├── static/
│   └── uploads/                      # 违规截图存储目录
└── database.db                       # SQLite数据库文件
```

## API接口设计

### 摄像头管理 API
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/cameras | 获取摄像头列表 |
| POST | /api/cameras | 添加摄像头 |
| PUT | /api/cameras/{id} | 编辑摄像头 |
| DELETE | /api/cameras/{id} | 删除摄像头 |
| GET | /api/cameras/{id}/test | 测试RTSP连接 |

### 区域管理 API
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/zones | 获取区域列表 |
| GET | /api/zones/{camera_id} | 获取指定摄像头的区域 |
| POST | /api/zones | 添加区域 |
| PUT | /api/zones/{id} | 编辑区域 |
| DELETE | /api/zones/{id} | 删除区域 |

### 违规记录 API
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/violations | 获取违规记录（支持分页、筛选） |
| GET | /api/violations/{id} | 获取记录详情 |
| DELETE | /api/violations/{id} | 删除记录 |
| POST | /api/violations/export | 导出数据（Excel/PDF/ZIP） |

### 统计分析 API
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/statistics/zone | 区域违规统计 |
| GET | /api/statistics/period | 时段违规统计（早/中/晚班） |
| GET | /api/statistics/camera | 摄像头违规统计 |
| GET | /api/statistics/trend | 违规趋势数据（日/周/月） |

### 实时推送
| 协议 | 路径 | 说明 |
|------|------|------|
| WS | /ws/detection | WebSocket实时推送检测结果 |

### 系统配置 API
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/config | 获取系统配置 |
| PUT | /api/config | 更新配置 |
| GET | /api/config/detection | 获取检测参数配置 |
| PUT | /api/config/detection | 更新检测参数 |
| POST | /api/config/backup | 备份数据库 |
| POST | /api/config/restore | 恢复数据库 |

### 通知消息 API
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/notifications | 获取通知列表 |
| GET | /api/notifications/unread-count | 获取未读数量 |
| PUT | /api/notifications/{id}/read | 标记为已读 |
| PUT | /api/notifications/read-all | 全部标记为已读 |
| DELETE | /api/notifications/{id} | 删除通知 |

### 摄像头状态 API
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/cameras/status | 获取所有摄像头状态（在线/离线） |

## 统计分析内容

| 图表类型 | 说明 | 展示形式 |
|---------|------|---------|
| 区域违规对比 | 各检测区域的违规次数对比，识别高风险区域 | 柱状图 |
| 时段违规分析 | 按早班/中班/晚班统计违规分布 | 饼图/柱状图 |
| 摄像头违规统计 | 每个摄像头对应的违规总数排行 | 横向柱状图 |
| 违规趋势图 | 按日/周/月的违规数量变化趋势 | 折线图 |

## 测试模式支持

系统支持三种视频源类型：

| 类型 | 说明 | 使用场景 |
|------|------|---------|
| RTSP流 | 标准RTSP协议视频流 | 生产环境 |
| 本地视频文件 | MP4等视频文件 | 测试环境 |
| USB摄像头 | 本地USB摄像头设备 | 开发调试 |

### 使用VLC模拟RTSP流进行测试

```bash
# 启动单路RTSP流
vlc -vvv "test_video.mp4" --sout "#rtp{sdp=rtsp://:8554/stream1}" --loop

# 启动多路RTSP流（模拟多个摄像头）
vlc -vvv "camera1_test.mp4" --sout "#rtp{sdp=rtsp://:8554/camera1}" --loop
vlc -vvv "camera2_test.mp4" --sout "#rtp{sdp=rtsp://:8554/camera2}" --loop
```

## 技术栈

| 层级 | 技术选型 |
|------|---------|
| 前端框架 | Vue 3 + Composition API |
| UI组件库 | Element Plus |
| 图表库 | ECharts |
| 状态管理 | Pinia |
| 后端框架 | FastAPI |
| ORM | SQLAlchemy |
| AI模型 | ultralytics YOLO 11M |
| 数据库 | SQLite |
| 视频处理 | OpenCV + FFmpeg |
| 实时通信 | WebSocket |
| 数据导出 | openpyxl (Excel), reportlab (PDF) |

## 关键技术实现

### 1. ROI绘制实现（前端）

使用 SVG + Canvas 实现：
1. 加载视频第一帧作为背景
2. SVG绘制多边形路径
3. 保存归一化坐标（0-1范围，适配不同分辨率）
4. 支持拖拽顶点编辑

### 2. RTSP流处理（后端）

使用 OpenCV + FFmpeg：
1. 通过 cv2.VideoCapture 读取RTSP
2. 开启独立线程处理每路视频
3. 转换为JPEG通过HTTP流式传输给前端

### 3. 违规去重机制

在检测到违规时：
- 记录 camera_id, zone_id, 检测框中心点坐标
- 如果配置时间内同一区域相近位置已有记录，则跳过
- 使用坐标距离判断是否为同一位置

## 验证计划

1. 启动系统，连接测试视频流
2. 添加摄像头配置
3. 配置ROI区域
4. 验证检测功能（佩戴/未佩戴头盔）
5. 验证违规记录保存和去重
6. 验证前端实时展示
7. 验证数据导出功能
8. 验证统计分析功能
