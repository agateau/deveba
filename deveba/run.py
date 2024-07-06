import os
import shlex
import subprocess

from typing import Mapping, List, Union, Optional

from pathlib import Path


class RunError(Exception):
    def __init__(
        self, cmd: List[str], proc: subprocess.CompletedProcess, cwd: str | None
    ):
        cmd_str = " ".join(shlex.quote(x) for x in cmd)
        if cwd is None:
            cwd = os.getcwd()
        msg = (
            f"Command '{cmd_str}' running in '{cwd}' failed.\n"
            f"exit code: {proc.returncode}\n"
            "stdout:\n"
            f"{proc.stdout}"
            "stderr:\n"
            f"{proc.stderr}"
        )
        Exception.__init__(self, msg)


def run(
    cmd: List[Union[str, Path]],
    *,
    cwd: Union[str, Path, None] = None,
    env: Optional[Mapping[str, str]] = None,
    merge_output: bool = False,
) -> subprocess.CompletedProcess:
    str_cmd: list[str] = [str(x) for x in cmd]
    if cwd is not None:
        cwd = str(cwd)
    proc = subprocess.run(
        str_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT if merge_output else subprocess.PIPE,
        env=env,
        cwd=cwd,
        text=True,
    )
    if proc.returncode != 0:
        raise RunError(str_cmd, proc, cwd)
    return proc
