import logging
import os
from logging.handlers import RotatingFileHandler

# 创建日志目录
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日志文件路径
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

def get_logger(name: str):
    """
    获取一个带有回滚机制的 Logger。

    :param name: 日志记录器的名称，一般为模块名。
    :return: Logger 对象。
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # 设置最低日志级别

    # 创建日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 控制台只输出 INFO 以上的日志
    console_handler.setFormatter(formatter)

    # 文件日志处理器，带有日志回滚
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)  # 日志文件最大5MB，保留3个文件
    file_handler.setLevel(logging.DEBUG)  # 文件中记录 DEBUG 及以上级别的日志
    file_handler.setFormatter(formatter)

    # 避免重复添加处理器
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
