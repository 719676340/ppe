# 制丝车间安全头盔智能检测系统

广西中烟南宁卷烟厂制丝车间安全头盔智能检测系统。

## 前置要求

### 后端
- Python 3.9 或更高版本
- pip (Python包管理器)

### 前端
- Node.js 16 或更高版本
- npm 或 yarn

## 快速开始

### 1. 克隆项目并配置环境

```bash
# 复制环境变量配置文件
cp .env.example .env

# 编辑 .env 文件，修改必要的配置（生产环境必须修改 SECRET_KEY）
```

### 2. 后端启动

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 http://localhost:8000 启动

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

## 技术栈
- 后端: FastAPI + YOLO 11M + OpenCV
- 前端: Vue 3 + Element Plus + ECharts
- 数据库: SQLite
