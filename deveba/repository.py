from path import path

class RepositoryError(Exception):
    pass

class Repository(object):
    """
    Base class for repositories
    """
    __slots__ = ["path", "group"]

    @classmethod
    def can_handle(self, path):
        """
        Must return True if it can handle the repository in path
        """
        raise NotImplementedError

    def __init__(self):
        self.path = path()
        self.group = None

    def __str__(self):
        return self.path

    def backup(self, proginfo):
        raise NotImplementedError
