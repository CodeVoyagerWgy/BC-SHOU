import requests
import json
import os
import ddddocr
import base64
import time
import schedule

from dotenv import load_dotenv, set_key

# 加载 .env 文件
load_dotenv()


# 全局常量
BASE_HEADERS = {
    'User-Agent': 'SWSuperApp/1.0.19 (iPad; iOS 18.0; Scale/2.00)'
}

ROOM_DATA = [{'id': '1805786225388752897', 'name': '羽毛球馆（第1片）', 'useRuleId': '1836673554756079618'},
             {'id': '1805786563000864769', 'name': '羽毛球馆（第2片）', 'useRuleId': '1836673554756079618'},
             {'id': '1805786726624858113', 'name': '羽毛球馆（第3片）', 'useRuleId': '1836673554756079618'},
             {'id': '1805786849387941890', 'name': '羽毛球馆（第4片）', 'useRuleId': '1836673554756079618'},
             {'id': '1805786997765640193', 'name': '羽毛球馆（第5片）', 'useRuleId': '1836673554756079618'},
             {'id': '1805787086051545090', 'name': '羽毛球馆（第6片）', 'useRuleId': '1836673554756079618'},
             {'id': '1805787158638170113', 'name': '羽毛球馆（第7片）', 'useRuleId': '1836673554756079618'},
             {'id': '1805787236174073857', 'name': '羽毛球馆（第8片）', 'useRuleId': '1836673554756079618'},
             {'id': '1805787290704220161', 'name': '羽毛球馆（第9片）', 'useRuleId': '1836673554756079618'},
             {'id': '1805787332970221569', 'name': '羽毛球馆（第10片）', 'useRuleId': '1836673554756079618'},
             {'id': '1805787783732072450', 'name': '羽毛球馆（第11片）', 'useRuleId': '1836673554756079618'},
             {'id': '1805788599830384641', 'name': '羽毛球馆（第17片）', 'useRuleId': '1799980541204172801'},
             {'id': '1805788636819951618', 'name': '羽毛球馆（第18片）', 'useRuleId': '1799980541204172801'},
             {'id': '1805788681132773378', 'name': '羽毛球馆（第19片）', 'useRuleId': '1799980541204172801'},
             {'id': '1805788719334494209', 'name': '羽毛球馆（第20片）', 'useRuleId': '1799980541204172801'},
             {'id': '1805788766054846465', 'name': '羽毛球馆（第21片）', 'useRuleId': '1799980541204172801'}]

# URL常量
MFA_URL = "https://uis.shou.edu.cn/token/mfa/detect"
LOGIN_URL = "https://uis.shou.edu.cn/token/password/passwordLogin"
QUERY_RESERVATION_URL = "https://meeting-reservation.shou.edu.cn/api/home/reserve4site"
CAPTCHA_URL_TEMPLATE = "https://meeting-reservation.shou.edu.cn/api/room/captcha/{}"
RESERVATION_URL = "https://meeting-reservation.shou.edu.cn/api/reservation"
MY_INFO_URL = "https://authx-service.shou.edu.cn/personal/api/v1/me/user"


def get_mfa(username, password):
    data = {
        "username": username,
        "password": password,
        'deviceId': 'DB9C9B29-85A7-44B2-907D-2D3F8BF1B371',
    }
    response = requests.post(MFA_URL, headers=BASE_HEADERS, data=data)
    json_data = json.loads(response.text)
    mfaState = json_data["data"]['state']
    return mfaState


# 登录函数
def login(username, password, mfaState):
    login_data = {
        'appId': 'com.supwisdom.ahd',
        'clientId': 'CLIENT_ID',
        # 'deviceId': 'BBE18D7D-6696-4B4C-828B-348A116CD485',
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
            print("登录成功")
            return session, response_body['data']['idToken']
        else:
            print(f"登录失败: {response_body.get('message', '未知错误')}")
            return None, None
    except requests.RequestException as e:
        print(f"登录请求失败，请检查密码是否正确: {e}")
        return None, None
    except json.JSONDecodeError:
        print("无法解析登录响应")
        return None, None


def get_info(session, token):
    query_headers = {**BASE_HEADERS, 'X-Id-Token': token}
    try:
        response = session.get(MY_INFO_URL, headers=query_headers)
        json_data = json.loads(response.text)
        leaderId = json_data['data']['attributes']['userId']
        userName = json_data['data']['attributes']['userName']
        applicant = json_data['data']['attributes']['organizationId']
        applicantLabel = json_data['data']['attributes']['organizationName']
    except requests.RequestException as e:
        print(f"查询失败: {e}")


# 查询预定函数
def query_reservation(name):
    for room in ROOM_DATA:
        if room['name'] == name:
            useRuleId = room['useRuleId']
            roomId = room['id']
            break
    else:
        raise ValueError(f"没有找到名称为{name}的房间")

    return  roomId,useRuleId


# 获取验证码函数
def get_captcha(session, token, room_id):
    captcha_url = CAPTCHA_URL_TEMPLATE.format(room_id)
    query_headers = {**BASE_HEADERS, 'X-Id-Token': token}

    try:
        response = session.get(captcha_url, headers=query_headers)
        response.raise_for_status()
        response_data = json.loads(response.text)

        if response_data['code'] == 200:
            return response_data['data']
        else:
            print(f"获取验证码错误: {response_data.get('msg', '未知错误')}")
            return ""
    except requests.RequestException as e:
        print(f"获取验证码失败: {e}")
        return ""


# OCR 识别验证码
def ocr_recognize(captcha_base64):
    ocr = ddddocr.DdddOcr()

    try:
        if captcha_base64.startswith('data:image'):
            captcha_base64 = captcha_base64.split(',')[1]
        image_data = base64.b64decode(captcha_base64)
        result = ocr.classification(image_data)
        print("OCR 识别结果:", result)
        return result
    except base64.binascii.Error as e:
        print(f"Base64 解码错误: {e}")
        return ""
    except Exception as e:
        print(f"OCR 识别错误: {e}")
        return ""


# 提交预约函数
def reserve(session, token, room_id, role_id,start_time, end_time, apply_date, retries=3):
    query_headers = {**BASE_HEADERS, 'X-Id-Token': token}
    try:
        response = session.get(MY_INFO_URL, headers=query_headers)
        json_data = json.loads(response.text)
        leaderId = json_data['data']['attributes']['userId']
        userName = json_data['data']['attributes']['userName']
        applicant = json_data['data']['attributes']['organizationId']
        applicantLabel = json_data['data']['attributes']['organizationName']
        print(f"用户ID:{leaderId};用户名称:{userName};学院编号:{applicant};学院名称:{applicantLabel}")
    except requests.RequestException as e:
        print(f"获取个人信息: {e}")

    captcha_base64 = get_captcha(session, token, room_id)

    if not captcha_base64:
        print("验证码获取失败，停止预约")
        return

    for attempt in range(retries):
        capacha_code = ocr_recognize(captcha_base64)
        if not capacha_code:
            print("验证码识别失败，停止预约")
            return

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
            "phone": os.getenv("PHONE", ""),
            "leaderNo": os.getenv("USERNAME", ""),
            "useRuleId": role_id,
            "remark": "",
            "applicantLabel": applicantLabel
        }

        query_headers = {**BASE_HEADERS, 'X-Id-Token': token}

        try:
            response = session.post(RESERVATION_URL, json=reservation_data, headers=query_headers)
            response_data = response.json()
            print(response_data)

            if response_data['code'] == 200:
                print("预约成功")
                break
            elif response_data['code'] == 400 and response_data['msg'] == '验证码错误':
                print(f"验证码错误，第 {attempt + 1}/{retries} 次重试")
                captcha_base64 = get_captcha(session, token, room_id)
            else:
                print(f"预约失败: {response_data.get('message', '未知错误')}")
                break
        except requests.RequestException as e:
            print(f"预约请求失败: {e}")
            break


def main():

    # 从 .env 文件中加载用户名和密码
    username = os.getenv("USERNAME", "")
    password = os.getenv("PASSWORD", "")
    token = os.getenv("TOKEN", None)  # 从 .env 文件读取 token

    # 从 .env 文件读取房间ID、开始时间、结束时间和预约日期
    room = os.getenv("ROOM", '羽毛球馆（第5片）')
    start_time = os.getenv("START_TIME", '18:00')
    end_time = os.getenv("END_TIME", '18:30')
    apply_date = os.getenv("APPLY_DATE", '2024-10-16')

    session = requests.session()

    # 如果没有 token，则进行登录操作
    if not token:
        mfaState = get_mfa(username, password)
        session, token = login(username, password, mfaState)
        if token:
            # 登录成功后，将 token 写入 .env 文件
            set_key('.env', 'TOKEN', token)
    else:
        print("使用已有的 TOKEN 进行操作")

    if session and token:
        room_id,role_id = query_reservation(room)
        flag = query_start(session, token, apply_date)
        while not flag:
            print_time_message("预约未开始...")
            time.sleep(10)
            flag = query_start(session, token, apply_date)
        print_time_message("预约已开始!!!")
        if room_id:
            print(f"查询到房间ID为:{room_id}")
            reserve(session, token, room_id, role_id,start_time, end_time, apply_date)
        else:
            print("房间查找失败")
def print_time_message(message):
    # 获取当前时间戳
    now = time.time()

    # 将时间戳转换为本地时间
    local_time = time.localtime(now)

    # 格式化时间输出
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)

def query_start(session, token, date):
    query_headers = {**BASE_HEADERS, 'X-Id-Token': token}
    params = {'projectId': '1800403370013822977', 'date': date}
    try:
        response = session.get(QUERY_RESERVATION_URL, headers=query_headers, params=params)
        data = json.loads(response.text)
        reservation_list = data['data']['30']['reservationList']
        isStarted = False

        for reservation in reservation_list:
            if reservation['timeRanges'] != None:
                print(reservation['timeRanges'])
                isStarted = True
                break
        return isStarted
    except requests.RequestException as e:
        print(f"查询失败: {e}")


if __name__ == '__main__':
    main()
    # 设置23点执行 start 函数
    # schedule.every().day.at("23:00").do(start)
    #
    # print("定时开启，23点开始预约")
    #
    # # 保持程序运行，直到任务执行完毕
    # while not done:
    #     schedule.run_pending()
    #     time.sleep(0.1)  # 减小睡眠时间以提高检查频率
    #
    # print("任务执行完毕，程序已退出")
