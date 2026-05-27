# LivePoll - 实时投票系统

基于 Django + Vue 3 的全栈实时投票平台，支持创建投票、实时更新结果、自动到期关闭等功能。

## 前置要求

- Python 3.13.5
- Node.js v22.17.1 和 npm
- Redis 5.0+（Windows 用户推荐 [Memurai](https://www.memurai.com/) 或通过 WSL 安装原生 Redis）

## 技术栈
- 后端：Django, Django REST Framework, Django Channels, Redis
- 前端：Vue 3, Vite, TypeScript, Pinia, Chart.js
- 数据库：SQLite

## 快速开始

### 1. 克隆仓库
git clone https://github.com/zzz2383/livepoll.git  

cd livepoll

## 一键部署（Docker Compose）

1. 安装 Docker 和 Docker Compose   

2. 启动所有服务：  

   ```bash  

   docker-compose --env-file .env.production up -d  


### 2. 后端设置
cd backend  

python -m venv venv  

venv\Scripts\activate  # Windows  

或者  

source venv/bin/activate  # Linux / macOS  

pip install -r requirements.txt  


python manage.py migrate  


# 确保 Redis 正在运行，默认端口 6379
redis-server  # 启动 Redis 服务，默认端口 6379（Linux / macOS）  


或者  
  
memurai.exe  # 启动 Memurai 服务，默认端口 6379（Windows）  

daphne config.asgi:application  # 启动后端服务，默认端口 8000  


### 3. 前端设置
cd frontend  

npm install  

npm run dev  

### 4. 访问
打开 http://localhost:3000