# 使用官方 Python 轻量级镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# 安装 poetry
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# 复制项目文件
COPY pyproject.toml poetry.lock* ./
COPY cf-dns-updater.py .
COPY log.py .

# 安装依赖
RUN poetry install --no-dev --no-root

# 创建数据卷，用于持久化存储 IP 缓存文件
VOLUME ["/app/data"]

# 设置入口点
ENTRYPOINT ["python", "cf-dns-updater.py"]

# 设置默认命令
CMD ["--help"]
