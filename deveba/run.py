import shlex
import subprocess

from typing import Mapping

from path import Path


class RunError(Exception):
    def __init__(self, cmd: list[str], proc: subprocess.CompletedProcess):
        cmd_str = " ".join(shlex.quote(x) for x in cmd)
        msg = (
            f"Command '{cmd_str}' failed with exit code {proc.returncode}\n"
            "{proc.stdout}"
        )
        Exception.__init__(self, msg)


def run(
    cmd: list[str | Path], cwd: str | None = None, env: Mapping[str, str] | None = None
) -> subprocess.CompletedProcess:
    str_cmd: list[str] = [str(x) for x in cmd]
    proc = subprocess.run(
        str_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        cwd=cwd,
        text=True,
    )
    if proc.returncode != 0:
        raise RunError(str_cmd, proc)
    return proc
