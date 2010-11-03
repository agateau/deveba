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
                if not proginfo.ok_to_commit():
                    logging.warning("Cancelled commit")
                    return
                logging.info("Committing changes")
                self.handler.commit()

            self.handler.fetch()

            if self.handler.need_merge():
                if not proginfo.ok_to_merge():
                    logging.warning("Cancelled merge")
                    return
                logging.info("Merging upstream changes")
                self.handler.merge()

            if self.handler.need_push():
                if not proginfo.ok_to_push():
                    logging.warning("Cancelled push")
                    return
                logging.info("Pushing changes")
                self.handler.push()

        except HandlerError, exc:
            logging.error("Failed: %s" % exc)
