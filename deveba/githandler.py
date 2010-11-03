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


class GitHandler(Handler):
    def work(self, path, proginfo, group):
        old_cwd = os.getcwd()
        git = GitRepo(path)

        self._commit(git, proginfo, group)
        self._pull(git)
        self._push(git)
        logging.info("Done")

    def _commit(self, git, proginfo, group):
        logging.info("Checking for changes")
        found_changes, new_files = git.get_status()
        if not found_changes:
            logging.info("No change found")
            return False
        if len(new_files) > 0:
            git.run_git("add", *new_files)

        msg = "Automatic commit from %s, running on %s (group %s)" % (proginfo.name, proginfo.hostname, group)
        author = "%s <%s@%s>" % (proginfo.name, proginfo.name, proginfo.hostname)
        git.run_git("commit", "-a", "-m", msg, "--author", author)
        logging.info("Committed changes")

        return True

    def _pull(self, git):
        logging.info("Updating copy")
        git.run_git("pull")

    def _push(self, git):
        if git.need_to_push():
            logging.info("Pushing changes")
            git.run_git("push")
        else:
            logging.info("Nothing to push")
