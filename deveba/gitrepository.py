import os
import logging

from shell import shell

from repository import Repository, RepositoryError

class GitRepo(object):
    """
    A low-level abstraction for a git repository
    """
    __slots__ = ["path"]
    def __init__(self, path):
        self.path = path

    @staticmethod
    def _run_git(*args):
        result = shell.git(*args)
        if result.returncode != 0:
            raise RepositoryError(result.stderr.strip())
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
        status = set()
        out = self.run_git("status", "--porcelain")
        if out == '':
            return False, []

        new_files = []
        for line in out.splitlines():
            if line.startswith("??"):
                name = line[3:]
                if name.startswith('"'):
                    # FIXME: Dangerous?
                    name = eval(name)
                new_files.append(name)
        return True, new_files

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

class GitRepository(Repository):
    __slots__ = ["repo"]

    @classmethod
    def can_handle(self, path):
        return (path / ".git").exists()

    def backup(self, proginfo):
        self.repo = GitRepo(self.path)
        found_changes, new_files = self.repo.get_status()

        if found_changes:
            if not proginfo.ok_to_commit():
                logging.warning("Cancelled commit")
                return
            logging.info("Committing changes")
            self._commit(proginfo, new_files)

        self.repo.run_git("fetch")

        if self.repo.need_merge():
            if not proginfo.ok_to_merge():
                logging.warning("Cancelled merge")
                return
            logging.info("Merging upstream changes")
            self.repo.run_git("merge", "origin/master")

        if self.repo.need_push():
            if not proginfo.ok_to_push():
                logging.warning("Cancelled push")
                return
            logging.info("Pushing changes")
            self.repo.run_git("push")

    def _commit(self, proginfo, new_files):
        if len(new_files) > 0:
            self.repo.add(*new_files)

        msg = "Automatic commit from %s, running on %s (group %s)" % (proginfo.name, proginfo.hostname, self.group)
        author = "%s <%s@%s>" % (proginfo.name, proginfo.name, proginfo.hostname)
        self.repo.commit(msg, "-a", "--author", author)
