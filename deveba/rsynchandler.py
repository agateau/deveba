from path import path
from shell import Command

from handler import Handler, HandlerError


def parse_path(repo_path):
    if not repo_path.startswith("rsync:"):
        return False
    return path(repo_path.split(":")[1]).expanduser()


class RsyncHandler(Handler):
    """
    Rsync handler
    Supported options:
    - destination: The destination file
    """
    __slots__ = ["_src", "_options"]

    def __init__(self, src):
        Handler.__init__(self)
        self._src = src
        self._options = {}

    @classmethod
    def create(cls, repo_path):
        if not repo_path.startswith("rsync:"):
            return None
        src = path(repo_path.split(":")[1]).expanduser()
        if src and src.exists():
            return RsyncHandler(src)
        else:
            return None

    def __str__(self):
        return "rsync: " + self._src

    def set_options(self, value):
        if not "destination" in value:
            raise HandlerError("rsync handler requires the 'destination' option")
        Handler.set_options(self, value)

    def sync(self, ui):
        cmd = Command("rsync")
        dst = path(self._options["destination"])
        result = cmd("-avzF", "--partial", "--delete", self._src + "/", dst)
        if result.returncode != 0:
            raise HandlerError("rsync failed with exit code %d.\n%s" % \
                (result.returncode, result.stderr))
