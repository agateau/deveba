import socket

class ProgInfo(object):
    __slots__ = "name", "hostname"

    def __init__(self):
        self.name = "deveba"
        self.hostname = socket.gethostname()
