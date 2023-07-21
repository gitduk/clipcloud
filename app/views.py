import pyperclip
from flask import Blueprint, request, current_app as app
from app.tasks import is_changed

bp = Blueprint("root", __name__, url_prefix="/")


@bp.route("/get_clipboard", methods=["GET", "POST"])
def get_clipboard():
    if is_changed.delay().get() == "YES":
        text = pyperclip.paste()
        app.logger.info(f"Sync: {text}")
        return text, 200
    else:
        return "", 200


@bp.route("/set_clipboard", methods=["GET", "POST"])
def set_clipboard():
    text = request.args.get("text", "")

    pyperclip.copy(text)
    app.logger.info(f"Set ClipBoard: {text}")

    return text
