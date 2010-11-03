import socket

"""
"dependency-injection object", used to pass various information about the
program and the way it interacts
"""
class ProgInfo(object):
    __slots__ = "name", "hostname"

    def __init__(self):
        self.name = "deveba"
        self.hostname = socket.gethostname()

    def ok_to_commit(self):
        return True

    def ok_to_merge(self):
        return True

    def ok_to_push(self):
        return True

def confirm(msg):
    line = raw_input("%s (Yn): " % msg)
    return line.lower() == "y"

"""
An implementation of ProgInfo which prompts before every changes
"""
class InteractiveProgInfo(ProgInfo):
    def ok_to_commit(self):
        return confirm("Uncommitted changes detected, commit them?")

    def ok_to_merge(self):
        return confirm("Upstream changes fetched, merge them?")

    def ok_to_push(self):
        return confirm("Local changes not pushed, push them?")
