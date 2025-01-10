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

## 日志

脚本使用了详细的日志记录，包括：
- 操作日志
- 错误信息
- API 调用结果

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
