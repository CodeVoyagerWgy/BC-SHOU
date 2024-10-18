

import requests
import json
from dotenv import set_key

from config import MFA_URL, LOGIN_URL, BASE_HEADERS
from logger import get_logger

logger = get_logger(__name__)


def get_mfa(username, password):
    data = {
        "username": username,
        "password": password,
        'deviceId': 'DB9C9B29-85A7-44B2-907D-2D3F8BF1B371',
    }
    response = requests.post(MFA_URL, headers=BASE_HEADERS, data=data)
    json_data = json.loads(response.text)
    return json_data["data"]['state']


def login(username, password, mfaState):
    login_data = {
        'appId': 'com.supwisdom.ahd',
        'clientId': 'CLIENT_ID',
        'deviceId': 'DB9C9B29-85A7-44B2-907D-2D3F8BF1B371',
        'mfaState': mfaState,
        'osType': 'iOS',
        'password': password,
        'username': username
    }

    try:
        session = requests.session()
        response = session.post(LOGIN_URL, data=login_data, headers=BASE_HEADERS)
        response.raise_for_status()
        response_body = response.json()

        if response_body['code'] == 0:
            logger.info("登录成功")
            set_key('.env', 'TOKEN', response_body['data']['idToken'])
            return session, response_body['data']['idToken']
        else:
            logger.error(f"登录失败: {response_body.get('message', '未知错误')}")
            return None, None
    except Exception as e:
        logger.error(f"登录请求失败: {e}")
        return None, None
