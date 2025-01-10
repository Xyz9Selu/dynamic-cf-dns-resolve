import click
import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from log import logger, action_logger

# 加载环境变量
load_dotenv()

# Cloudflare API 配置
api_token = os.getenv("CF_API_TOKEN")
zone_id = os.getenv("CF_ZONE_ID")
record_id = os.getenv("CF_RECORD_ID")
domain = os.getenv("CF_DOMAIN")
ip_cache_file = os.getenv("IP_CACHE_FILE", "/tmp/last_ip.txt")

# 邮件配置
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT", "587"))
email_user = os.getenv("EMAIL_USER")
email_pass = os.getenv("EMAIL_PASS")
recipient_email = os.getenv("RECIPIENT_EMAIL")

# 获取当前外网 IP
@action_logger("获取当前外网IP")
def get_public_ip():
    response = requests.get("https://ifconfig.me", timeout=10)
    return response.text.strip()

# 从 Cloudflare 获取 DNS 记录
@action_logger("从Cloudflare获取DNS记录")
def get_cloudflare_record():
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    result = response.json()
    
    if result.get("success"):
        ip = result["result"]["content"]
        return ip
    else:
        return None

# 读取本地缓存的上次 IP，如果读取失败则从 Cloudflare 获取
@action_logger("读取本地缓存的上次IP")
def get_cached_ip():
    # 首先尝试从缓存文件读取
    if os.path.exists(ip_cache_file):
        with open(ip_cache_file, "r") as file:
            return file.read().strip()
    
    # 如果缓存读取失败，从 Cloudflare 获取
    ip = get_cloudflare_record()
    if ip:
        # 更新缓存文件
        update_cached_ip(ip)
    return ip

# 更新本地缓存的 IP
@action_logger("更新本地缓存的IP")
def update_cached_ip(ip):
    with open(ip_cache_file, "w") as file:
        file.write(ip)

# 更新 Cloudflare DNS 记录
@action_logger("更新Cloudflare DNS记录")
def update_dns_record(ip):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    data = {"type": "A", "name": domain, "content": ip, "ttl": 1, "proxied": False}
    response = requests.put(url, json=data, headers=headers)
    result = response.json()
    if result.get("success"):
        return result
    else:
        raise Exception("DNS记录更新失败")

# 发送邮件通知
@action_logger("发送邮件通知")
def send_email(subject, body):
    # 检查邮件配置是否完整
    if not all([smtp_server, smtp_port, email_user, email_pass, recipient_email]):
        logger.info("邮件配置不完整，跳过发送邮件通知")
        return
    
    msg = MIMEMultipart()
    msg["From"] = email_user
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_user, email_pass)
        server.send_message(msg)

# 使用 Click 构建命令行工具
@click.group()
def cli():
    """Cloudflare DNS 更新脚本"""
    pass

@cli.command()
def get_ip():
    """获取当前外网 IP"""
    click.echo(f"当前外网 IP: {get_public_ip()}")

@cli.command()
def get_cache():
    """获取本地缓存的 IP"""
    cached_ip = get_cached_ip()
    if cached_ip:
        click.echo(f"缓存的 IP: {cached_ip}")
    else:
        click.echo("没有找到缓存的 IP")

@cli.command()
@click.option("--ip", required=True, help="要更新到缓存的 IP 地址")
def update_cache(ip):
    """更新本地缓存的 IP"""
    update_cached_ip(ip)
    click.echo(f"缓存已更新为: {ip}")

@cli.command()
@click.option("--ip", required=True, help="要更新到 DNS 的 IP 地址")
def update_dns(ip):
    """更新 Cloudflare DNS 记录"""
    result = update_dns_record(ip)
    if result.get("success"):
        click.echo(f"DNS 更新成功: {ip}")
    else:
        click.echo(f"DNS 更新失败: {result}")

@cli.command()
def get_cf_record():
    """从 Cloudflare 获取当前 DNS 记录"""
    ip = get_cloudflare_record()
    if ip:
        click.echo(f"Cloudflare DNS记录中的IP: {ip}")
    else:
        click.echo("无法从Cloudflare获取DNS记录")

@cli.command()
@click.option("--subject", required=True, help="邮件主题")
@click.option("--body", required=True, help="邮件正文")
def send_email_command(subject, body):
    """发送邮件通知"""
    send_email(subject, body)
    click.echo("邮件已发送")

@cli.command()
def full_run():
    """完整运行脚本：检测 IP 变化、更新 DNS 和发送通知"""
    current_ip = get_public_ip()
    cached_ip = get_cached_ip()
    if current_ip == cached_ip:
        click.echo("IP 未变化，无需更新")
    else:
        click.echo(f"IP 变化检测到: {current_ip}")
        result = update_dns_record(current_ip)
        if result.get("success"):
            click.echo(f"DNS 更新成功: {current_ip}")
            update_cached_ip(current_ip)
            send_email("Cloudflare 更新成功通知", f"新 IP 为: {current_ip}")
        else:
            click.echo("DNS 更新失败")
            send_email("Cloudflare 更新失败通知", "更新 DNS 记录时发生错误")

if __name__ == "__main__":
    cli()
