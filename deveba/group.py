class Group(object):
    __slots__ = ["name", "repositories"]

    def __init__(self):
        self.name = ""
        self.repositories = {}

    def __str__(self):
        return self.name

    def backup(self, proginfo):
        for repo in self.repositories.values():
            repo.backup(proginfo)
