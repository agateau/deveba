from svn.constants import ST_MISSING, ST_UNVERSIONED
from svn.exception import SvnException
from svn.local import LocalClient

from deveba import utils
from deveba.handler import Handler, HandlerError


def call_delete(repo, path):
    # PySvn currently does not expose the `delete` command. Until one of the
    # opened PR to implement it is merged, let's do it manually
    repo.run_command("delete", [path], wd=repo.path)


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
            # Handle local changes first, otherwise removed files are brought
            # back by the update
            local_changes = []
            for entry in self.repo.status():
                change = f"{entry.name}: {entry.type_raw_name}"
                local_changes.append(change)
                if entry.type == ST_UNVERSIONED:
                    self.repo.add(entry.name)
                elif entry.type == ST_MISSING:
                    call_delete(self.repo, entry.name)

            ui.log_verbose("Updating")
            self.repo.update()

            if local_changes:
                ui.log_verbose("Local changes:\n" + "\n".join(local_changes))
                msg = utils.generate_commit_message(self.group)
                ui.log_verbose("Committing changes")
                self.repo.commit(msg)
            else:
                ui.log_verbose("No local changes")

        except SvnException as exc:
            raise HandlerError(str(exc)) from None
