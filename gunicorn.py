import os

# 定义同时开启的处理请求的进程数量，根据网站流量适当调整
workers = 5
# 采用gevent库，支持异步处理请求，提高吞吐量
worker_class = "gevent"
bind = f"{os.environ.get('HOST', '0.0.0.0')}:{os.environ.get('PORT', 5000)}"

