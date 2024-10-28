

import os
import time


import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta


from login import get_mfa, login
from query_start import query_start
from reservation import reserve
from config import ROOM_DATA
from logger import get_logger

logger = get_logger(__name__)
# Setup logging


def main():
    load_dotenv()
    username = os.getenv("USERNAME", "")
    password = os.getenv("PASSWORD", "")
    token = os.getenv("TOKEN", None)

    room = os.getenv("ROOM", 'default_room')
    start_time = os.getenv("START_TIME", '18:00')
    end_time = os.getenv("END_TIME", '18:30')
    apply_date = os.getenv("APPLY_DATE", '2024-10-16')
    phone = os.getenv("PHONE", "")

    session = requests.session()

    three_days_later = datetime.now() + timedelta(days=3)

    # 格式化日期为YYYY-MM-DD
    formatted_date = three_days_later.strftime('%Y-%m-%d')

    if not token:
        logger.info("未发现Token，尝试登录")
        mfa_state = get_mfa(username, password)
        session, token = login(username, password, mfa_state)

    if session and token:
        try:
            room_id, role_id = next((r['id'], r['useRuleId']) for r in ROOM_DATA if r['name'] == room)
        except StopIteration:
            logger.error(f"Room {room} not found in ROOM_DATA.")
            return

        flag = query_start(session, token, apply_date)
        while not flag:
            logger.info("预约未开始，等待中...")
            time.sleep(5)
            flag = query_start(session, token, apply_date)
        # 优先预约设定的房间
        result = reserve(session, token, room_id, role_id, start_time, end_time, apply_date, phone)
        # 设定的房间没有预约成功，尝试预约其他房间
        if(result==2):
            for room in ROOM_DATA:
                result =reserve(session, token, room[id], role_id, start_time, end_time, apply_date, phone)
                if(result!=2):
                    break
if __name__ == '__main__':
    main()




