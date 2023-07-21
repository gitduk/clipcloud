FROM python:3.10

WORKDIR /app
RUN apt-get update && \
    apt-get install -y xclip && \
    rm -rf /var/lib/apt/lists/*

COPY . /app
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 5000

