from deveba.run import run, RunError

from deveba.handler import Handler, HandlerError


class UnisonHandler(Handler):
    """
    Unison handler
    Supported options:
    - type: "unison"
    - path: the profile name
    - version: if set, the name of the unison binary is set to
      "unison-$version" instead of "unison"
    """

    __slots__ = ["_bin_name", "_profile"]

    def __init__(self, profile, version):
        Handler.__init__(self)
        self._profile = profile
        self._bin_name = "unison"
        if version:
            self._bin_name += "-" + version

    @classmethod
    def create(cls, repo_path, options):
        if options.get("type") != "unison":
            return None
        return UnisonHandler(repo_path, options.get("version"))

    def __str__(self):
        return f"{self._bin_name}: {self._profile}"

    def sync(self, ui):
        cmd = [self._bin_name, "-ui", "text", "-terse", "-batch", self._profile]
        try:
            run(cmd)
        except RunError as exc:
            raise HandlerError(exc) from None
