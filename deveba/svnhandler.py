from svn.constants import ST_UNVERSIONED
from svn.exception import SvnException
from svn.local import LocalClient

from deveba import utils
from deveba.handler import Handler, HandlerError


class SvnHandler(Handler):
    __slots__ = ["repo"]

    def __init__(self, repo_path):
        Handler.__init__(self)
        self.repo = LocalClient(repo_path)

    @classmethod
    def create(cls, repo_path, options):
        if not (repo_path / ".svn").exists():
            return None
        return SvnHandler(repo_path)

    def __str__(self):
        return "svn: " + self.repo.path

    def sync(self, ui):
        try:
            ui.log_verbose("Updating")
            self.repo.update()

            local_changes = []
            for entry in self.repo.status():
                local_changes.append("{}: {}".format(entry.name, entry.type_raw_name))
                if entry.type == ST_UNVERSIONED:
                    self.repo.add(entry.name)

            if local_changes:
                ui.log_verbose("Local changes:\n" + "\n".join(local_changes))
                msg = utils.generate_commit_message(self.group)
                ui.log_verbose("Committing changes")
                self.repo.commit(msg)
            else:
                ui.log_verbose("No local changes")
        except SvnException as exc:
            raise HandlerError(str(exc))
