import pyperclip
from celery import shared_task
from flask import current_app as app


@shared_task(ignore_result=False)
def is_changed():
    rds = app.extensions["redis"]
    current_text = pyperclip.paste()
    if current_text != rds.get("clip_text").decode():
        rds.set("clip_text", current_text)
        return "YES"
    return "NO"
