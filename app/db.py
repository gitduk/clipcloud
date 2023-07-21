from flask_redis import FlaskRedis


def init_redis(app):
    app.extensions["redis"] = FlaskRedis(app)
    app.extensions["redis"].init_app(app)
    return app.extensions["redis"]

