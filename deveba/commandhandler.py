import os
import subprocess

from handler import Handler, HandlerError


class CommandHandler(Handler):
    """
    Generic command handler
    Supported options:
    - type: "command"
    - path: Where to run the command
    - command: The command to run
    """
    __slots__ = ["_path", "_command"]

    def __init__(self, path, command):
        Handler.__init__(self)
        self._path = path
        self._command = command

    @classmethod
    def create(cls, repo_path, options):
        if options.get("type") != "command":
            return None
        try:
            command = options["command"]
        except KeyError as exc:
            raise HandlerError("Missing required option: command")
        if not repo_path.exists():
            raise HandlerError("Invalid path '%s'".format(repo_path))
        return CommandHandler(repo_path, command)

    def __str__(self):
        return "command: {} {}".format(self._path, self._command)

    def sync(self, ui):
        old_cwd = os.getcwd()
        os.chdir(self._path)
        try:
            subprocess.check_output(self._command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as exc:
            raise HandlerError("Command failed with exit code %d.\n%s" % \
                (exc.returncode, exc.output))
        finally:
            os.chdir(old_cwd)
