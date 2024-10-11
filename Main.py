import requests
import json
import os


def login(username, password):
    login_url = "https://uis.shou.edu.cn/token/password/passwordLogin"
    login_headers = {
        'User-Agent': 'SWSuperApp/1.0.19 (iPad; iOS 18.0; Scale/2.00)'
    }
    login_data = {
        'appId': 'com.supwisdom.ahd',
        'clientId': 'CLIENT_ID',
        'deviceId': 'BBE18D7D-6696-4B4C-828B-348A116CD485&mfaState=9zT101',
        '&osType': 'iOS',
        'password': password,
        'username': username
    }

    try:
        session = requests.session()
        response = session.post(login_url, data=login_data, headers=login_headers)
        response.raise_for_status()  # 检查请求是否成功
        response_body = response.json()  # 使用 response.json() 简化 json.loads()

        if response_body['code'] == 0:
            print("登录成功")
            return session, response_body['data']['idToken']
        else:
            print("登录失败:", response_body.get('message', '未知错误'))
            return None, None
    except requests.RequestException as e:
        print(f"登录请求失败: {e}")
        return None, None
    except json.JSONDecodeError:
        print("无法解析登录响应")
        return None, None


def query_reservation(session, token, date):
    query_url = "https://meeting-reservation.shou.edu.cn/api/home/reserve4site"
    query_headers = {
        'User-Agent': 'SWSuperApp/1.0.19 (iPad; iOS 18.0; Scale/2.00)',
        'X-Id-Token': token
    }
    params = {
        'projectId': '1800403370013822977',
        'date': date
    }

    try:
        response = session.get(query_url, headers=query_headers, params=params)
        response.raise_for_status()
        print(response.text)
    except requests.RequestException as e:
        print(f"查询失败: {e}")


if __name__ == "__main__":
    # 从环境变量或其他安全方式获取密码
    username = os.getenv("USERNAME", "m220951640")
    password = os.getenv("PASSWORD", "wangguiyou123")

    session, token = login(username, password)
    if session and token:
        query_reservation(session, token, '2024-10-13')
