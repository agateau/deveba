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
    __slots__ = ["path", "group", "options"]

    @classmethod
    def can_handle(cls, path):
        """
        Must return True if this class can handle the content of 'path'
        """
        raise NotImplementedError

    def __init__(self):
        self.path = path()
        self.group = None
        self.options = {}

    def __str__(self):
        txt = self.path
        if self.options:
            txt += " (%s)" % self.options
        return txt

    def sync(self, ui):
        raise NotImplementedError
