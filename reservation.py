import requests
import json

from config import BASE_HEADERS, MY_INFO_URL, RESERVATION_URL
from captcha import get_captcha
from utils import ocr_recognize
from logger import get_logger

logger = get_logger(__name__)

def reserve(session, token, room_id, role_id, start_time, end_time, apply_date, phone):
    query_headers = {**BASE_HEADERS, 'X-Id-Token': token}

    try:
        response = session.get(MY_INFO_URL, headers=query_headers)
        json_data = json.loads(response.text)
        leaderId = json_data['data']['attributes']['userId']
        userName = json_data['data']['attributes']['userName']
        applicant = json_data['data']['attributes']['organizationId']
        applicantLabel = json_data['data']['attributes']['organizationName']
        logger.info(f"用户ID: {leaderId}, 用户名: {userName}, 学院编号: {applicant}, 学院名称: {applicantLabel}")
    except Exception as e:
        logger.error(f"获取个人信息失败: {e}")
        return

    retry_count = 0
    max_retries = 3

    while retry_count < max_retries:
        captcha_base64 = get_captcha(session, token, room_id)
        if not captcha_base64:
            logger.error("验证码获取失败")
            return

        capacha_code = ocr_recognize(captcha_base64)
        if not capacha_code:
            retry_count += 1
            logger.error(f"验证码识别失败，重试中... ({retry_count}/{max_retries})")
            continue  # 继续循环，重新获取验证码并识别

        reservation_data = {
            "leaderName": userName,
            "leaderId": leaderId,
            "actualUserPhone": "",
            "captcha": capacha_code,
            "docUrl": [],
            "actualUserName": "",
            "participant": [],
            "applyExtendList": [
                {
                    "seatNumber": "",
                    "endTime": end_time,
                    "applyDate": apply_date,
                    "beginTime": start_time
                }
            ],
            "subject": "羽毛球运动",
            "actualUserAccountName": "",
            "applicant": applicant,
            "roomId": room_id,
            "allowAgentRa": 0,
            "actualUserId": "",
            "participantLeader": [],
            "isCycle": 0,
            "seatCount": 4,
            "phone": phone,
            "leaderNo": userName,
            "useRuleId": role_id,
            "remark": "",
            "applicantLabel": applicantLabel
        }

        try:
            response = session.post(RESERVATION_URL, json=reservation_data, headers=query_headers)
            response_data = response.json()

            if response_data['code'] == 200:
                logger.info(f"预约成功")
                return  1# 成功预约后，退出循环
            elif response_data['code'] == 400 and response_data['msg'] == '验证码错误':
                retry_count += 1
                logger.error(f"验证码错误，重试中... ({retry_count}/{max_retries})")
            elif response_data['code'] == 400 and '已被其他人预约' in str(response_data['msg']):
                # 切换房间号重新预约
                logger.error(f"预约时间段已满")
                return 2
            else:
                logger.error(f"预约失败: 状态码-{response_data['code']};{response_data.get('msg', '未知错误')}")
                return -1

        except Exception as e:
            retry_count += 1
            logger.error(f"预约请求失败: {e}，重试中... ({retry_count}/{max_retries})")

    logger.error(f"预约失败，已结束")
    return -1
