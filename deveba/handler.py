from path import path

class HandlerError(Exception):
    pass

class Handler(object):
    """
    Base class for repository handlers
    """
    __slots__ = ["path", "group"]

    @classmethod
    def can_handle(cls, path):
        """
        Must return True if this class can handle the content of 'path'
        """
        raise NotImplementedError

    def __init__(self):
        self.path = path()
        self.group = None

    def __str__(self):
        return self.path

    def backup(self, proginfo, ui):
        raise NotImplementedError
