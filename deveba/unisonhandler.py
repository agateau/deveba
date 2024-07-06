from path import Path

from deveba.run import run, RunError

from deveba.handler import Handler, HandlerError


def profile_for_path(path):
    if not path.startswith("unison:"):
        return None
    return path.split(":")[1]


class UnisonHandler(Handler):
    """
    Unison handler
    Supported options:
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
        profile = profile_for_path(repo_path)
        if profile is None:
            return None
        if Path(f"~/.unison/{profile}.prf").expanduser().exists():
            return UnisonHandler(profile, options.get("version"))
        else:
            return None

    def __str__(self):
        return self._bin_name + ": " + self._profile

    def sync(self, ui):
        cmd = [self._bin_name, "-ui", "text", "-terse", "-batch", self._profile]
        try:
            run(cmd)
        except RunError as exc:
            raise HandlerError(exc) from None
