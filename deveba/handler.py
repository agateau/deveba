class HandlerError(Exception):
    pass

class Handler(object):
    __slots__ = ["path", "proginfo", "group"]
    def init(self, path, proginfo, group):
        self.path = path
        self.proginfo = proginfo
        self.group = group

    def need_commit(self):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def fetch(self):
        raise NotImplementedError

    def need_merge(self):
        raise NotImplementedError

    def merge(self):
        raise NotImplementedError

    def need_push(self):
        raise NotImplementedError

    def push(self):
        raise NotImplementedError

