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

    __slots__ = ["group"]

    @classmethod
    def create(cls, repo_path, options):
        """
        Must return an instance of this class if it can handle the directory at
        `repo_path` using options from the `options` dictionary
        """
        raise NotImplementedError

    def __init__(self):
        self.group = None

    def sync(self, ui):
        raise NotImplementedError
