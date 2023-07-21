from app import clr
from app.tasks import is_changed


@clr.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # sender.add_periodic_task(1, is_changed.s(), name="listen clipboard")
    pass
