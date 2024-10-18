import requests
import json

from config import CAPTCHA_URL_TEMPLATE, BASE_HEADERS
from utils import ocr_recognize
from logger import get_logger

logger = get_logger(__name__)


def get_captcha(session, token, room_id):
    captcha_url = CAPTCHA_URL_TEMPLATE.format(room_id)
    query_headers = {**BASE_HEADERS, 'X-Id-Token': token}

    try:
        response = session.get(captcha_url, headers=query_headers)
        response.raise_for_status()
        response_data = json.loads(response.text)

        if response_data['code'] == 200:
            logger.info("获取验证码成功")
            return response_data['data']
        else:
            logger.error(f"获取验证码失败: {response_data.get('msg', '未知错误')}")
            return ""
    except requests.RequestException as e:
        logger.error(f"获取验证码失败: {e}")
        return ""

