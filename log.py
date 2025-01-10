# 配置日志
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from functools import wraps
import os
import pathlib

app_name = os.getenv("APP_NAME", pathlib.Path(__file__).parent.name)
log_dir = os.getenv("LOG_DIR", "./logs")
max_log_size = os.getenv("LOG_MAX_SIZE", 10*1024*1024)
backup_count = os.getenv("LOG_BACKUP_COUNT", 12)

def setup_logging():
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # 生成当前月份的日志文件名
    current_month = datetime.now().strftime("%Y-%m")
    log_file = log_path / f"{app_name}-{current_month}.log"
    
    # 配置日志处理器
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_log_size,  # 10MB
        backupCount=backup_count,  # 保留12个备份文件
        encoding='utf-8'
    )
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # 配置logger
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    return logger

# 初始化日志
logger = setup_logging()

def action_logger(action_name=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"""{action_name or func.__name__}开始 {f'args: {args}' if args else ''} {f'kwargs: {kwargs}' if kwargs else ''}""")
            try: 
                result = func(*args, **kwargs)
                logger.info(f"""{action_name or func.__name__}成功{f': {result}' if result else ''}""")
                return result
            except Exception as e:
                logger.error(f"""{action_name or func.__name__}失败: {str(e)}""")
                raise
        return wrapper
    return decorator
