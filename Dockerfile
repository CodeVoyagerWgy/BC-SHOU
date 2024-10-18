# 使用官方的 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目的所有文件到容器中
COPY . /app

# 拷贝 .env 文件到容器中（如果有本地 .env 文件的话）
COPY .env /app/.env

# 安装所需的 Python 依赖，使用国内镜像源
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 运行容器时，容器中运行的命令
CMD ["python", "main.py"]