# 制丝车间安全头盔智能检测系统

广西中烟南宁卷烟厂制丝车间安全头盔智能检测系统，采用深度学习技术实时检测作业人员安全帽佩戴情况。

## 功能特性

- 实时视频流处理与检测
- 多路摄像头同时监控
- 多边形检测区域自定义
- 智能违规去重记录
- 违规截图自动保存
- 多维度统计分析
- Excel数据导出

## 技术栈

- **后端**: FastAPI + YOLO v11 + OpenCV + SQLAlchemy
- **前端**: Vue 3 + Element Plus + ECharts + Pinia
- **数据库**: SQLite

---

## 环境要求

### 硬件要求
- CPU: Intel Core i5 及以上
- 内存: 8GB 及以上，推荐 16GB
- 硬盘: 100GB 可用空间，推荐 SSD 256GB
- 网络: 100Mbps 及以上

### 软件要求
- **Conda**: Miniconda 或 Anaconda
- **Node.js**: 16+ (用于前端开发)
- **Git**: 用于版本管理

---

## 安装部署

### 1. 获取项目代码

```bash
# 克隆项目
git clone <项目地址>
cd 头盔
```

### 2. 创建 Conda 环境

```bash
# 创建名为 helmet-detection 的 conda 环境，Python 版本 3.9
conda create -n helmet-detection python=3.9 -y

# 激活环境
conda activate helmet-detection
```

### 3. 安装后端依赖

```bash
cd backend

# 安装 Python 依赖
pip install -r requirements.txt

# 验证安装
python -c "import fastapi; import ultralytics; print('依赖安装成功')"
```

### 4. 配置环境变量

```bash
# 在 backend 目录下创建 .env 文件
cat > .env << EOF
# 数据库配置
DATABASE_URL=sqlite:///./helmet_detection.db

# JWT 密钥（生产环境请修改为随机字符串）
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 检测模型配置
MODEL_PATH=models/yolo11n.pt
CONFIDENCE_THRESHOLD=0.5
IOU_THRESHOLD=0.45

# 文件存储路径
UPLOAD_DIR=./uploads
VIOLATION_IMAGES_DIR=./violation_images
EXPORT_DIR=./exports

# 服务器配置
HOST=0.0.0.0
PORT=8000
EOF
```

### 5. 安装前端依赖

```bash
cd ../frontend

# 安装 npm 依赖
npm install
```

### 6. 创建必要目录

```bash
cd ../backend

# 创建数据存储目录
mkdir -p uploads violation_images exports models
```

---

## 启动系统

### 方式一：开发模式

**终端1 - 启动后端:**
```bash
# 确保 conda 环境已激活
conda activate helmet-detection

cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**终端2 - 启动前端:**
```bash
cd frontend
npm run dev
```

### 方式二：生产模式

**后端启动:**
```bash
conda activate helmet-detection
cd backend
# 不使用 --reload，使用多 worker
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**前端构建与部署:**
```bash
cd frontend

# 构建生产版本
npm run build

# 使用 nginx 或其他 web 服务器部署 dist 目录
```

---

## 使用指南

### 首次使用流程

#### 1. 登录系统
访问 `http://localhost:5173`，使用默认账号登录：
- 用户名: `admin`
- 密码: `admin`

#### 2. 添加摄像头
1. 进入「摄像头管理」页面
2. 点击「添加摄像头」
3. 填写摄像头信息：
   - 摄像头名称：如「制丝车间1号机」
   - 视频源地址：如 `rtsp://192.168.1.100:554/stream`
   - 是否启用：勾选则自动启动检测
4. 点击确定保存

#### 3. 配置检测区域
1. 进入「区域管理」页面
2. 选择要配置的摄像头
3. 点击「添加区域」
4. 在视频画面上点击绘制检测区域（至少3个点）
5. 填写区域名称，如「1号机工作区」
6. 点击确定保存

#### 4. 启动检测
1. 进入「实时监控」页面
2. 选择要启动的摄像头
3. 点击「启动检测」按钮
4. 系统开始实时检测，显示结果：
   - **绿色框**: 已佩戴安全帽
   - **红色框**: 未佩戴安全帽（违规）
   - **黄色多边形**: 检测区域

#### 5. 查看违规记录
1. 进入「违规管理」页面
2. 系统显示所有违规记录
3. 可以查看违规截图、添加备注、标记处理状态
4. 支持导出Excel报告

---

## 目录结构

```
头盔/
├── backend/                    # 后端代码
│   ├── main.py                # 主程序入口
│   ├── config.py              # 配置管理
│   ├── requirements.txt       # Python依赖
│   ├── detection/             # 检测模块
│   │   ├── detector.py        # PPE检测器
│   │   ├── stream_processor.py # 视频流处理
│   │   ├── violation_recorder.py # 违规记录
│   │   └── roi_manager.py     # 区域管理
│   ├── management/            # 管理模块
│   │   ├── database.py        # 数据库模型
│   │   ├── routers/           # API路由
│   │   └── services/          # 业务服务
│   ├── uploads/               # 上传文件
│   ├── violation_images/      # 违规截图
│   └── exports/               # 导出文件
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   ├── components/        # 通用组件
│   │   ├── stores/            # Pinia状态管理
│   │   └── utils/             # 工具函数
│   ├── package.json           # npm依赖
│   └── vite.config.js         # Vite配置
└── copyright-application-materials/  # 软著申请材料
```

---

## 常见问题

### Q1: conda 环境激活失败
```bash
# 初始化 conda (如果未初始化)
conda init zsh  # 或 bash, fish 等
# 重启终端后生效
```

### Q2: 检测模型下载失败
```bash
# 手动下载 YOLO 模型到 backend/models/ 目录
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolo11n.pt -P backend/models/
```

### Q3: 视频流无法连接
- 检查摄像头网络连接
- 确认视频源地址格式正确（rtsp/http）
- 检查防火墙设置

### Q4: 检测延迟过高
- 减少同时检测的摄像头数量
- 降低视频分辨率
- 使用 GPU 加速（需要安装 CUDA 版本的 PyTorch）

---

## 开发说明

### 后端 API 文档
启动后端后访问 `http://localhost:8000/docs` 查看自动生成的 API 文档。

### 前端开发
```bash
cd frontend
npm run dev    # 开发模式
npm run build  # 生产构建
```

### 代码风格
- Python: 遵循 PEP 8 规范
- JavaScript: 使用 ESLint 配置

---

## 版本历史

- **v1.0.0** - 2024年12月
  - 初始版本
  - 实现核心检测功能
  - 完成前后端基础界面

---

## 许可证

本项目为内部使用系统，版权归广西中烟南宁卷烟厂所有。
