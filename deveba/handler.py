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
    __slots__ = ["group", "_options"]

    @classmethod
    def create(cls, path):
        """
        Must return an instance of this class if it can handle the content of 'path'
        """
        raise NotImplementedError

    def __init__(self):
        self.group = None
        self._options = {}

    def get_options(self):
        return self._options

    def set_options(self, value):
        self._options = value
    options = property(get_options, set_options)

    def sync(self, ui):
        raise NotImplementedError
