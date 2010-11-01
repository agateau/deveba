class Group(object):
    __slots__ = ["name", "_repositories"]

    def __init__(self):
        self.name = ""
        self._repositories = {}

    def repositories(self):
        return self._repositories.values()

    def add_repository(self, repo):
        self._repositories[repo.path] = repo

    def __str__(self):
        return self.name

    def backup(self, proginfo):
        for repo in self._repositories.values():
            repo.backup(proginfo)
