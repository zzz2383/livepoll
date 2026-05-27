FROM python:3.13.5-slim

# 设置国内 pip 源（阿里云）
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY . .

# 暴露端口（Daphne 默认 8000）
EXPOSE 8000

# 启动命令
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]