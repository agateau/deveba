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
    __slots__ = ["_profile"]

    def __init__(self, profile):
        Handler.__init__(self)
        self._profile = profile

    @classmethod
    def create(cls, repo_path):
        profile = profile_for_path(repo_path)
        if profile is None:
            return False
        if path("~/.unison/%s.prf" % profile).expanduser().exists():
            return UnisonHandler(profile)
        else:
            return None

    def __str__(self):
        bin_name = "unison"
        if "version" in self.options:
            bin_name += "-" + self.options["version"]
        return bin_name + ": " + self._profile

    def sync(self, ui):
        bin_name = "unison"
        if "version" in self.options:
            bin_name += "-" + self.options["version"]

        cmd = Command(bin_name)
        try:
            result = cmd("-ui", "text", "-terse", "-batch", self._profile)
        except OSError, exc:
            if exc.errno == errno.ENOENT:
                raise HandlerError("Failed to find or run a binary named %s" % bin_name)
        if result.returncode != 0:
            raise HandlerError("unison failed with errorcode %d.\n%s" % \
                (result.returncode, result.stderr))
