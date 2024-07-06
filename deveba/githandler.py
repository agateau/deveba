import os

from deveba.shell import shell

from deveba import utils
from deveba.handler import Handler, HandlerError, HandlerConflictError


class GitStatus:
    """
    Parses the output of git status --porcelain -z into usable fields
    """

    __slots__ = ["modified_files", "new_files", "conflicting_files"]

    def __init__(self, out):
        """
        out is the output of `git status --porcelain -z`
        """

        CONFLICT_STATES = [
            "DD",
            "AU",
            "UD",
            "UA",
            "DU",
            "AA",
            "UU",
        ]
        self.modified_files = []
        self.new_files = []
        self.conflicting_files = []

        for line in out.split("\0"):
            if len(line) == 0:
                continue
            state = line[:2]
            name = line[3:]
            if state == "??":
                self.new_files.append(name)
            elif state in CONFLICT_STATES:
                self.conflicting_files.append(name)
            else:
                self.modified_files.append(name)

    def has_changes(self):
        return (
            bool(self.modified_files)
            or bool(self.new_files)
            or bool(self.conflicting_files)
        )


class GitRepo:
    """
    Helper class to run git commands
    """

    __slots__ = ["path"]

    def __init__(self, path):
        self.path = path

    @staticmethod
    def _run_git(*args):
        result = shell.git(*args)
        if result.returncode != 0:
            out = str(result.stdout, "utf-8").strip()
            err = str(result.stderr, "utf-8").strip()
            msg = []
            arg_str = " ".join(args)
            msg.append(f"command: `git {arg_str}`")
            if out:
                msg.append(f"stdout: {out}")
            if err:
                msg.append(f"stderr: {err}")
            raise HandlerError("\n".join(msg))
        return str(result.stdout, "utf-8")

    def run_git(self, *args):
        old_cwd = os.getcwd()
        os.chdir(self.path)
        try:
            return GitRepo._run_git(*args)
        finally:
            os.chdir(old_cwd)

    @staticmethod
    def clone(remote_repository_path, repository_path, *args):
        GitRepo._run_git("clone", remote_repository_path, repository_path, *args)
        return GitRepo(repository_path)

    def get_status(self):
        out = self.run_git("status", "--porcelain", "-z")
        return GitStatus(out)

    def need_push(self):
        out = self.run_git("rev-list", "origin/master..")
        return len(out.strip()) > 0

    def add(self, *files):
        self.run_git("add", *files)

    def commit(self, msg, *args):
        self.run_git("commit", "-m", msg, *args)

    def need_merge(self):
        out = self.run_git("rev-list", "..origin/master")
        return len(out.strip()) > 0

    def merge(self, remote):
        try:
            self.run_git("merge", remote)
        except HandlerError:
            status = self.get_status()
            if status.conflicting_files:
                raise HandlerConflictError(status.conflicting_files)
            else:
                # Something else happened
                raise


class GitHandler(Handler):
    __slots__ = ["repo"]

    def __init__(self, repo_path):
        Handler.__init__(self)
        self.repo = GitRepo(repo_path)

    @classmethod
    def create(cls, repo_path, options):
        if not (repo_path / ".git").exists():
            return None
        return GitHandler(repo_path)

    def __str__(self):
        return "git: " + self.repo.path

    def sync(self, ui):
        def format_list(lst):
            return "\n".join("- " + x for x in lst)

        status = self.repo.get_status()

        if status.has_changes():
            while True:
                modified_str = format_list(status.modified_files)
                new_str = format_list(status.new_files)
                ui.log_verbose(
                    f"Modified files:\n{modified_str}\n\nNew files:\n{new_str}\n"
                )
                choices = ["Commit", "Show Diff"]
                answer = ui.question("Uncommitted changes detected", choices, "Commit")
                if answer == "Commit":
                    ui.log_info("Committing changes")
                    self._commit(status.new_files)
                    break
                elif answer == "Show Diff":
                    ui.log_verbose(self.repo.run_git("diff"))
                elif answer == ui.CANCEL:
                    ui.log_warning("Cancelled commit")
                    break

        self.repo.run_git("fetch")

        if self.repo.need_merge():
            if not ui.confirm("Upstream changes fetched, merge them?", True):
                ui.log_warning("Cancelled merge")
                return
            ui.log_info("Merging upstream changes")
            self.repo.merge("origin/master")

        if self.repo.need_push():
            if not ui.confirm("Local changes not pushed, push them?", True):
                ui.log_warning("Cancelled push")
                return
            ui.log_info("Pushing changes")
            self.repo.run_git("push")

    def _commit(self, new_files):
        if len(new_files) > 0:
            self.repo.add(*new_files)

        msg = utils.generate_commit_message(self.group)
        name = utils.get_commit_author_name()
        email = utils.get_commit_author_email()
        author = f"{name} <{email}>"
        self.repo.commit(msg, "-a", "--author", author)
