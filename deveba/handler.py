from path import path

class HandlerError(Exception):
    pass


class HandlerConflictError(HandlerError):
    __slots__ = ["conflicting_files"]
    def __init__(self, files):
        self.conflicting_files = files

    def __str__(self):
        return "conflicting files: %s" % self.conflicting_files


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

    def backup(self, ui):
        raise NotImplementedError
