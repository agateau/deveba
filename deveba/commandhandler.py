import os
import subprocess

from deveba.handler import Handler, HandlerError


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
        except KeyError:
            raise HandlerError("Missing required option: command")
        if not repo_path.exists():
            raise HandlerError(f"Invalid path '{repo_path}'")
        return CommandHandler(repo_path, command)

    def __str__(self):
        return f"command: {self._path} {self._command}"

    def sync(self, ui):
        old_cwd = os.getcwd()
        os.chdir(self._path)
        try:
            subprocess.check_output(self._command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as exc:
            raise HandlerError(
                f"Command failed with exit code {exc.returncode}.\n{exc.output}"
            )
        finally:
            os.chdir(old_cwd)
