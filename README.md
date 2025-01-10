# Dynamic Cloudflare DNS Resolver

一个用于动态更新 Cloudflare DNS 记录的 Python 脚本。支持 IP 缓存、DNS 记录更新以及邮件通知功能。

## 功能特点

- 获取当前公网 IP
- 从本地缓存或 Cloudflare 获取 DNS 记录
- 自动更新 Cloudflare DNS 记录
- 支持邮件通知
- 完整的命令行接口

## 环境要求

- Python 3.6+
- pip 包管理器

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

在项目根目录创建 `.env` 文件，配置以下环境变量：

```env
# Cloudflare API 配置
CF_API_TOKEN=your_api_token
CF_ZONE_ID=your_zone_id
CF_RECORD_ID=your_record_id
CF_DOMAIN=your.domain.com
IP_CACHE_FILE=/path/to/cache/file.txt  # 可选，默认为 /tmp/last_ip.txt

# 邮件配置（可选）
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
EMAIL_USER=your_email@example.com
EMAIL_PASS=your_email_password
RECIPIENT_EMAIL=recipient@example.com
```

## 使用方法

### 获取当前公网 IP
```bash
python cf-dns-updater.py get-ip
```

### 获取缓存的 IP
```bash
python cf-dns-updater.py get-cache
```

### 获取 Cloudflare DNS 记录
```bash
python cf-dns-updater.py get-cf-record
```

### 更新缓存的 IP
```bash
python cf-dns-updater.py update-cache --ip <IP地址>
```

### 更新 DNS 记录
```bash
python cf-dns-updater.py update-dns --ip <IP地址>
```

### 发送邮件通知
```bash
python cf-dns-updater.py send-email --subject "主题" --body "内容"
```

### 完整运行（检测IP变化并更新）
```bash
python cf-dns-updater.py full-run
```

## Docker 部署

### 构建镜像
```bash
docker build -t cf-dns-updater .
```

### 运行容器

有两种方式可以运行容器：

#### 1. 使用环境变量
```bash
docker run --rm \
  -e CF_API_TOKEN=your_api_token \
  -e CF_ZONE_ID=your_zone_id \
  -e CF_RECORD_ID=your_record_id \
  -e CF_DOMAIN=your.domain.com \
  -e SMTP_SERVER=smtp.example.com \
  -e SMTP_PORT=587 \
  -e EMAIL_USER=your_email@example.com \
  -e EMAIL_PASS=your_email_password \
  -e RECIPIENT_EMAIL=recipient@example.com \
  -v /path/to/host/logs:/app/logs \
  cf-dns-updater
```

#### 2. 使用 .env 文件
```bash
docker run --rm \
  --env-file .env \
  -v /path/to/host/logs:/app/logs \
  cf-dns-updater
```

### 重要说明

1. 日志目录挂载
   - 建议将容器内的 `/app/logs` 目录挂载到主机目录
   - 这样可以方便查看日志文件并进行日志轮转
   - 示例：`-v /path/to/host/logs:/app/logs`

## 定时任务配置

### Crontab 设置
```bash
# 编辑 crontab
crontab -e

# 添加以下内容（每5分钟执行一次）
*/5 * * * * docker run --rm --env-file /path/to/.env -v /path/to/host/logs:/app/logs cf-dns-updater python cf-dns-updater.py full-run

# 或者使用环境变量方式
*/5 * * * * docker run --rm -e CF_API_TOKEN=your_token -e CF_ZONE_ID=your_zone_id -e CF_RECORD_ID=your_record_id -e CF_DOMAIN=your.domain.com -v /path/to/host/logs:/app/logs cf-dns-updater python cf-dns-updater.py full-run
```

### 说明
- `*/5 * * * *`: 表示每5分钟执行一次
- `--rm`: 容器运行完成后自动删除
- 根据实际情况调整执行频率和配置路径
- 建议将执行频率设置在 5-15 分钟之间

## 日志

脚本使用了详细的日志记录，包括：
- 操作日志
- 错误信息
- API 调用结果

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
