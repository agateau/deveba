class Group(object):
    """
    Represent a group of repository handlers from the config file
    """

    __slots__ = ["name", "handlers"]

    def __init__(self):
        self.name = ""
        self.handlers = []

    def __str__(self):
        return self.name
