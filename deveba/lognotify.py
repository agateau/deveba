import logging
try:
    import pynotify
    HAS_PYNOTIFY = True
except ImportError:
    HAS_PYNOTIFY = False


class LogNotifyHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level)

    def emit(self, record):
        if record.levelno <= logging.INFO:
            icon = "dialog-information"
        elif record.levelno <= logging.WARNING:
            icon = "dialog-warning"
        else:
            icon = "dialog-error"
        notification = pynotify.Notification("Deveba", record.getMessage(), icon)
        notification.show()

def create_handler():
    if not HAS_PYNOTIFY:
        return None

    return LogNotifyHandler()
