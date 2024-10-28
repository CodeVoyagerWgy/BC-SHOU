FROM python:3.9-slim

WORKDIR /app

COPY . /app

COPY .env /app/.env

RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

CMD ["python", "main.py"]