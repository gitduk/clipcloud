from celery import Celery, Task


def init_celery(app):
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    clr = Celery(app.name, task_cls=FlaskTask)
    clr.config_from_object(app.config["CELERY"])
    clr.set_default()
    app.extensions["celery"] = clr
    return clr

