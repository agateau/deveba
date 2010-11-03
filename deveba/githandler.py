import logging
import os

from shell import shell

from handler import Handler, HandlerError

class GitRepo(object):
    __slots__ = ["path"]
    def __init__(self, path):
        self.path = path

    def _run_git(*args):
        result = shell.git(*args)
        if result.returncode != 0:
            raise HandlerError(result.stderr.strip())
        return result.stdout
    _run_git = staticmethod(_run_git)

    def run_git(self, *args):
        old_cwd = os.getcwd()
        os.chdir(self.path)
        try:
            return GitRepo._run_git(*args)
        finally:
            os.chdir(old_cwd)

    def clone(remote_repository_path, repository_path, *args):
        GitRepo._run_git("clone", remote_repository_path, repository_path, *args)
        return GitRepo(repository_path)
    clone = staticmethod(clone)

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

    def need_to_push(self):
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
    def init(self, path, proginfo, group):
        Handler.init(self, path, proginfo, group)
        self.repo = GitRepo(path)
        self.found_changes, self.new_files = self.repo.get_status()

    def need_commit(self):
        return self.found_changes

    def commit(self):
        if len(self.new_files) > 0:
            self.repo.add(self.new_files)

        msg = "Automatic commit from %s, running on %s (group %s)" % (self.proginfo.name, self.proginfo.hostname, self.group)
        author = "%s <%s@%s>" % (self.proginfo.name, self.proginfo.name, self.proginfo.hostname)
        self.repo.commit(msg, "--author", author)

    def fetch(self):
        self.repo.run_git("fetch")

    def need_merge(self):
        self.repo.need_merge()

    def merge(self):
        self.repo.run_git("merge", "origin/master")

    def need_push(self):
        return self.repo.need_to_push()

    def push(self):
        self.repo.run_git("push")
