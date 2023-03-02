# syntax=docker/dockerfile:1
FROM python:3.10-slim-bullseye

# 设定时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 设定国内 debian 的镜像源，参考：https://mirrors.tuna.tsinghua.edu.cn/help/debian/
RUN rm -rf /etc/apt/sources.list
COPY ./sources.list /etc/apt/

WORKDIR /code
RUN pip install --upgrade pip -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host=mirrors.aliyun.com
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host=mirrors.aliyun.com
COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app", "-k", "uvicorn.workers.UvicornWorker"]
