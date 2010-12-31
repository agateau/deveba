import os
import logging

from shell import shell

import utils
from handler import Handler, HandlerError

class GitStatus(object):
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
        return bool(self.modified_files) or bool(self.new_files) or bool(self.conflicting_files)

class GitRepo(object):
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
            out = result.stdout.strip()
            err = result.stderr.strip()
            msg = []
            if out:
                msg.append("stdout: %s" % out)
            if err:
                msg.append("stderr: %s" % err)
            raise HandlerError("\n".join(msg))
        return result.stdout

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

class GitHandler(Handler):
    __slots__ = ["repo"]

    @classmethod
    def can_handle(cls, path):
        return (path / ".git").exists()

    def backup(self, ui):
        def format_list(lst):
            return "\n".join("- " + x for x in lst)

        self.repo = GitRepo(self.path)
        status = self.repo.get_status()

        if status.has_changes():
            while True:
                ui.show_text("Modified files:\n%s\n\nNew files:\n%s\n"
                    % (format_list(status.modified_files), format_list(status.new_files))
                    )
                choices = ["Commit", "Show Diff"]
                answer = ui.question("Uncommitted changes detected", choices, "Commit")
                if answer == "Commit":
                    logging.info("Committing changes")
                    self._commit(status.new_files)
                    break
                elif answer == "Show Diff":
                    ui.show_text(self.repo.run_git("diff"))
                elif answer == ui.CANCEL:
                    logging.warning("Cancelled commit")
                    break

        self.repo.run_git("fetch")

        if self.repo.need_merge():
            if not ui.confirm("Upstream changes fetched, merge them?", True):
                logging.warning("Cancelled merge")
                return
            logging.info("Merging upstream changes")
            self.repo.run_git("merge", "origin/master")

        if self.repo.need_push():
            if not ui.confirm("Local changes not pushed, push them?", True):
                logging.warning("Cancelled push")
                return
            logging.info("Pushing changes")
            self.repo.run_git("push")

    def _commit(self, new_files):
        if len(new_files) > 0:
            self.repo.add(*new_files)

        msg = utils.generate_commit_message(self.group)
        author = "%s <%s>" % (utils.get_commit_author_name(), utils.get_commit_author_email())
        self.repo.commit(msg, "-a", "--author", author)
