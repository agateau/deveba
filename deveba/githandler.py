import logging
import os

from shell import shell

from handler import Handler, HandlerError

def run_git(*args):
    result = shell.git(*args)
    if result.returncode != 0:
        raise HandlerError(result.stderr.strip())
    return result.stdout

def get_status():
    status = set()
    out = run_git("status", "--porcelain")
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

class GitHandler(Handler):
    def work(self, path, proginfo, group):
        old_cwd = os.getcwd()
        os.chdir(path)

        try:
            self._commit(proginfo, group)
            logging.info("Updating copy")
            self._pull()
            logging.info("Pushing changes")
            self._push()
            logging.info("Done")
        finally:
            os.chdir(old_cwd)

    def _commit(self, proginfo, group):
        logging.info("Checking for changes")
        found_changes, new_files = get_status()
        if not found_changes:
            logging.info("No change found")
            return False
        if len(new_files) > 0:
            run_git("add", *new_files)

        msg = "Automatic commit from %s, running on %s (group %s)" % (proginfo.name, proginfo.hostname, group)
        author = "%s <%s@%s>" % (proginfo.name, proginfo.name, proginfo.hostname)
        run_git("commit", "-a", "-m", msg, "--author", author)
        logging.info("Committed changes")

        return True

    def _pull(self):
        run_git("pull")

    def _push(self):
        run_git("push")
