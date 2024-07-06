from typing import List

from deveba.handler import Handler


class Group:
    """
    Represent a group of repository handlers from the config file
    """

    __slots__ = ["name", "handlers"]

    def __init__(self):
        self.name = ""
        self.handlers: List[Handler] = []

    def __str__(self):
        return self.name
