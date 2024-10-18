import requests
import json

# 导入全局常量和URL
from config import BASE_HEADERS, QUERY_RESERVATION_URL

from logger import get_logger

logger = get_logger(__name__)

def query_start(session, token, date):
    """
    查询预约是否已经开始

    :param session: 已经登录的 session
    :param token: 登录获取的 token
    :param date: 预约日期
    :return: 如果预约已经开始，返回 True，否则返回 False
    """
    query_headers = {**BASE_HEADERS, 'X-Id-Token': token}
    params = {'projectId': '1800403370013822977', 'date': date}

    try:
        response = session.get(QUERY_RESERVATION_URL, headers=query_headers, params=params)
        response.raise_for_status()
        data = response.json()

        # 检查是否有可用的预约时间段
        reservation_list = data.get('data', {}).get('30', {}).get('reservationList', [])
        is_started = False

        for reservation in reservation_list:
            if reservation.get('timeRanges'):
                logger.info(f"预约时间段: {reservation['timeRanges']}")
                is_started = True
                break

        return is_started

    except requests.RequestException as e:
        logger.error(f"查询失败: {e}")
        return False
    except json.JSONDecodeError:
        logger.error("无法解析查询响应")
        return False
