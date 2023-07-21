import os
from flask import Flask
from app.config import config
from app.views import bp

from app.db import init_redis
from app.celery import init_celery
from app.cologer import init_logger


def create_app(name="default"):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # config flask
    app.config.from_mapping(
        SECRET_KEY="dev"
    )
    app.config.from_object(config.get(name))
    app.config.from_prefixed_env()

    register_api(app)
    register_extensions(app)
    register_commands(app)

    @app.route("/hello", methods=["GET", "POST"])
    def hello():
        return "hello flask!"

    @app.route("/route", methods=["GET", "POST"])
    def get_bp_urls():
        return [str(p) for p in app.url_map.iter_rules()]

    return app


def register_api(app):
    """
    注册蓝图
    """
    app.register_blueprint(bp)


def register_extensions(app):
    """
    注册插件
    """

    init_redis(app)
    init_celery(app)
    init_logger(app)


def register_commands(app):
    """
    注册命令
    """
    pass


app = create_app()
clr = app.extensions["celery"]
clr.autodiscover_tasks(["app.tasks"])

