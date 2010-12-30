class Group(object):
    __slots__ = ["name", "handlers"]

    def __init__(self):
        self.name = ""
        self.handlers = {}

    def __str__(self):
        return self.name
