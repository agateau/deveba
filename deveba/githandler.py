import os
import logging

from shell import shell

import utils
from handler import Handler, HandlerError

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
            raise HandlerError(result.stderr.strip())
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
        def clean_line(line):
            name = line[3:]
            if name.startswith('"'):
                # FIXME: Dangerous?
                name = eval(name)
            return name

        status = set()
        out = self.run_git("status", "--porcelain")
        if out == '':
            return False, [], []

        new_files = []
        modified_files = []
        for line in out.splitlines():
            if line.startswith("??"):
                new_files.append(clean_line(line))
            else:
                modified_files.append(clean_line(line))
        return True, modified_files, new_files

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
        found_changes, modified_files, new_files = self.repo.get_status()

        if found_changes:
            while True:
                ui.show_text("Modified files:\n%s\n\nNew files:\n%s\n"
                    % (format_list(modified_files), format_list(new_files))
                    )
                choices = ["Commit", "Show Diff"]
                answer = ui.question("Uncommitted changes detected", choices, "Commit")
                if answer == "Commit":
                    logging.info("Committing changes")
                    self._commit(new_files)
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
