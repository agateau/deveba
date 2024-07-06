import re
from functools import cached_property
from pathlib import Path
from typing import Optional

from deveba.handler import HandlerError, HandlerConflictError
from deveba.run import run, RunError


class GitStatus:
    """
    Parses the output of git status --porcelain -z into usable fields
    """

    __slots__ = ["modified_files", "new_files", "conflicting_files"]

    def __init__(self, out):
        """
        out is the output of `git status --porcelain -z`
        """

        CONFLICT_STATES = [
            "DD",
            "AU",
            "UD",
            "UA",
            "DU",
            "AA",
            "UU",
        ]
        self.modified_files = []
        self.new_files = []
        self.conflicting_files = []

        for line in out.split("\0"):
            if len(line) == 0:
                continue
            state = line[:2]
            name = line[3:]
            if state == "??":
                self.new_files.append(name)
            elif state in CONFLICT_STATES:
                self.conflicting_files.append(name)
            else:
                self.modified_files.append(name)

    def has_changes(self):
        return (
            bool(self.modified_files)
            or bool(self.new_files)
            or bool(self.conflicting_files)
        )


class GitRepo:
    """
    Helper class to run git commands
    """

    def __init__(self, path: Path):
        self.path = path

    @cached_property
    def default_branch(self) -> str:
        output = self.run_git("ls-remote", "--symref", "origin", "HEAD")

        # `output` looks like this:
        #
        # ref: refs/heads/master\tHEAD
        # d7511c76395ec4e8c2607ff5a55487190457d178\tHEAD
        #
        # We want the part after "refs/heads/"
        match = re.search(r"^ref: refs/heads/([^\t]+)\t", output)
        if not match:
            raise HandlerError(f"Can't read default branch from {output}")

        return match.group(1)

    @staticmethod
    def _run_git(*args, cwd: Optional[Path] = None):
        try:
            result = run(["git", *args], cwd=cwd)
        except RunError as exc:
            raise HandlerError(exc) from None
        return result.stdout

    def run_git(self, *args):
        return GitRepo._run_git(*args, cwd=self.path)

    @staticmethod
    def clone(remote_repository_path, repository_path, *args):
        GitRepo._run_git("clone", remote_repository_path, repository_path, *args)
        return GitRepo(repository_path)

    def get_status(self):
        out = self.run_git("status", "--porcelain", "-z")
        return GitStatus(out)

    def need_push(self):
        out = self.run_git("rev-list", f"origin/{self.default_branch}..")
        return len(out.strip()) > 0

    def add(self, *files):
        self.run_git("add", *files)

    def commit(self, msg, *args):
        self.run_git("commit", "-m", msg, *args)

    def need_merge(self):
        out = self.run_git("rev-list", f"..origin/{self.default_branch}")
        return len(out.strip()) > 0

    def merge(self, remote):
        try:
            self.run_git("merge", remote)
        except HandlerError:
            status = self.get_status()
            if status.conflicting_files:
                raise HandlerConflictError(status.conflicting_files) from None
            else:
                # Something else happened
                raise
