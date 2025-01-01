import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import schedule
import time
from login import get_mfa, login
from query_start import query_start
from reservation import reserve
from config import ROOM_DATA
from logger import get_logger

logger = get_logger(__name__)


def reserveTask():
    load_dotenv()
    username = os.getenv("USERNAME", "")
    password = os.getenv("PASSWORD", "")
    token = os.getenv("TOKEN", None)

    room = os.getenv("ROOM", 'default_room')
    start_time = os.getenv("START_TIME", '18:00')
    end_time = os.getenv("END_TIME", '18:30')
    phone = os.getenv("PHONE", "")

    session = requests.session()
    apply_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')

    # 检查并获取Token
    if not token:
        logger.info("未发现Token，尝试登录")
        mfa_state = get_mfa(username, password)
        session, token = login(username, password, mfa_state)

    if session and token:
        room_data = next((r for r in ROOM_DATA if r['name'] == room), None)
        if not room_data:
            logger.error(f"Room {room} not found in ROOM_DATA.")
            return

        # 等待预约开始
        while not query_start(session, token, apply_date):
            logger.info("预约未开始，等待中...")
            time.sleep(3)

        # 预约指定房间
        result = reserve(session, token, room_data['id'], room_data['useRuleId'], start_time, end_time, apply_date,
                         phone)

        # 若指定房间未预约成功，尝试其他房间
        if result == 2:
            for alt_room in ROOM_DATA:
                result = reserve(session, token, alt_room['id'], alt_room['useRuleId'], start_time, end_time,
                                 apply_date, phone)
                if result != 2:
                    break


def schedule_daily_task(task, hour, minute):
    schedule_time = f"{hour:02}:{minute:02}"
    schedule.every().day.at(schedule_time).do(task)
    logger.info(f"程序运行时间： {schedule_time}")
    now = datetime.now()
    if now.hour > hour or (now.hour == hour and now.minute >= minute):
        task()

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    schedule_daily_task(reserveTask, 20, 0)
