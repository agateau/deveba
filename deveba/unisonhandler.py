import errno

from path import path
from shell import Command

from handler import Handler, HandlerError

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
        if path("~/.unison/%s.prf" % profile).expanduser().exists():
            return UnisonHandler(profile, options.get("version"))
        else:
            return None

    def __str__(self):
        return self._bin_name + ": " + self._profile

    def sync(self, ui):
        cmd = Command(self._bin_name)
        try:
            result = cmd("-ui", "text", "-terse", "-batch", self._profile)
        except OSError, exc:
            if exc.errno == errno.ENOENT:
                raise HandlerError("Failed to find or run a binary named %s" % self._bin_name)
        if result.returncode != 0:
            raise HandlerError("unison failed with errorcode %d.\n%s" % \
                (result.returncode, result.stderr))
