from path import Path
from deveba.shell import Command

from deveba.handler import Handler, HandlerError


def parse_path(repo_path):
    if not repo_path.startswith("rsync:"):
        return False
    return Path(repo_path.split(":")[1]).expanduser()


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
            dst = Path(options["destination"]).expanduser()
        except KeyError:
            raise HandlerError("Missing required option: destination") from None
        return RsyncHandler(repo_path, dst)

    def __str__(self):
        return "rsync: " + self._src

    def sync(self, ui):
        cmd = Command("rsync")
        result = cmd("-avzF", "--partial", "--delete", self._src + "/", self._dst)
        if result.returncode != 0:
            raise HandlerError(
                f"rsync failed with exit code {result.returncode}.\n{result.stderr}"
            ) from None
