from path import Path

from deveba.run import run, RunError

from deveba.handler import Handler, HandlerError


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
        return f"rsync: {self._src}"

    def sync(self, ui):
        cmd = ["rsync", "-avzF", "--partial", "--delete", self._src + "/", self._dst]
        try:
            run(cmd)
        except RunError as exc:
            raise HandlerError(exc) from None
