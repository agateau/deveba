import logging

from handler import HandlerError
from githandler import GitHandler
from repository import Repository

class GitRepository(Repository):
    @classmethod
    def can_handle(self, path):
        return (path / ".git").exists()

    def backup(self, proginfo):
        handler = GitHandler()

        try:
            handler.init(self.path, proginfo, self.group.name)
            if handler.need_commit():
                if not proginfo.ok_to_commit():
                    logging.warning("Cancelled commit")
                    return
                logging.info("Committing changes")
                handler.commit()

            handler.fetch()

            if handler.need_merge():
                if not proginfo.ok_to_merge():
                    logging.warning("Cancelled merge")
                    return
                logging.info("Merging upstream changes")
                handler.merge()

            if handler.need_push():
                if not proginfo.ok_to_push():
                    logging.warning("Cancelled push")
                    return
                logging.info("Pushing changes")
                handler.push()

        except HandlerError, exc:
            logging.error("Failed: %s" % exc)
