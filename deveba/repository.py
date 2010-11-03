import logging

from path import path

from handler import HandlerError
from githandler import GitHandler

class Repository(object):
    __slots__ = ["path", "group", "handler"]

    def __init__(self):
        self.path = path()
        self.group = None
        self.handler = None

    def __str__(self):
        return self.path

    def backup(self, proginfo):
        logging.info("Starting work on %s" % self.path)
        if not self.path.exists():
            logging.error("Directory does not exist '%s'" % self.path)
            return
        if not self.handler:
            if (self.path / ".git").exists():
                self.handler = GitHandler()
            else:
                logging.error("Don't know how to handle directory '%s'" % self.path)
                return

        try:
            self.handler.init(self.path, proginfo, self.group.name)
            if self.handler.need_commit():
                logging.info("Committing changes")
                self.handler.commit()

            self.handler.fetch()

            if self.handler.need_merge():
                logging.info("Merging upstream changes")
                self.handler.merge()

            if self.handler.need_push():
                logging.info("Pushing changes")
                self.handler.push()

        except HandlerError, exc:
            logging.error("Failed: %s" % exc)
