import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 全局常量
BASE_HEADERS = {
    'User-Agent': 'SWSuperApp/1.0.19 (iPad; iOS 18.0; Scale/2.00)'
}

# 球场数据
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


