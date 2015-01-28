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
    __slots__ = ["src", "_options"]

    REQUIRED_OPTIONS = ["destination"]

    def __init__(self):
        self._options = {}

    @classmethod
    def can_handle(cls, repo_path):
        repo_path = parse_path(repo_path)
        return repo_path and repo_path.exists()

    def get_options(self):
        return self._options

    def set_options(self, value):
        if not "destination" in value:
            raise HandlerError("rsync handler requires the 'destination' option")
        self._options = value
    options = property(get_options, set_options)

    def sync(self, ui):
        cmd = Command("rsync")
        src = parse_path(self.path)
        src += "/"
        dst = path(self._options["destination"])
        result = cmd("-avzF", "--partial", "--delete", src, dst)
        if result.returncode != 0:
            raise HandlerError("rsync failed with exit code %d.\n%s" % \
                (result.returncode, result.stderr))
