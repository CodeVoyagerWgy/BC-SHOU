FROM python:3.9-slim

WORKDIR /app

COPY . /app
COPY .env /app/.env

RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 设置时区为东八区（CST）
RUN ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone

CMD ["python", "main.py"]