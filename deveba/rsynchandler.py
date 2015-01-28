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
    - type: "rsync"
    - path: The source dir
    - destination: The destination dir
    """
    __slots__ = ["_src", "_dst"]

    def __init__(self, src, dst):
        Handler.__init__(self)
        self._src = src
        self._dst = dst

    @classmethod
    def create(cls, repo_path, options):
        if options.get("type") != "rsync":
            return None
        try:
            dst = options["destination"]
        except KeyError as exc:
            raise HandlerError("Missing required option: destination")
        if not repo_path.exists():
            raise HandlerError("Invalid source directory '%s'".format(repo_path))
        return RsyncHandler(repo_path, dst)

    def __str__(self):
        return "rsync: " + self._src

    def sync(self, ui):
        cmd = Command("rsync")
        result = cmd("-avzF", "--partial", "--delete", self._src + "/", self._dst)
        if result.returncode != 0:
            raise HandlerError("rsync failed with exit code %d.\n%s" % \
                (result.returncode, result.stderr))
