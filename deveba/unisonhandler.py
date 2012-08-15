from path import path
from shell import Command

from handler import Handler, HandlerError

def profile_for_path(path):
    if not path.startswith("unison:"):
        return None
    return path.split(":")[1]

class UnisonHandler(Handler):
    __slots__ = ["repo"]

    @classmethod
    def can_handle(cls, repo_path):
        profile = profile_for_path(repo_path)
        if profile is None:
            return False
        return path("~/.unison/%s.prf" % profile).expanduser().exists()

    def sync(self, ui):
        bin_name = "unison"
        if "version" in self.options:
            bin_name += "-" + self.options["version"]

        cmd = Command(bin_name)
        profile = profile_for_path(self.path)
        result = cmd("-ui", "text", "-terse", "-batch", profile)
        if result.returncode != 0:
            raise HandlerError("unison failed with errorcode %d.\n%s" % \
                (result.returncode, result.stderr))
