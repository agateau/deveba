from pathlib import Path
from typing import List

from deveba.gitrepo import GitRepo


def write_file(name, content=""):
    with open(name, "w") as f:
        f.write(content)


def create_repository(sandbox: Path):
    origin_repo_path = sandbox / "repo.git"
    origin_repo_path.mkdir()
    origin_repo = GitRepo(origin_repo_path)
    origin_repo.run_git("init", "--bare")

    repo = GitRepo.clone(origin_repo.path, sandbox / "repo", "--no-hardlinks")
    write_file(repo.path / "dummy")
    repo.add("dummy")
    repo.commit("created")
    repo.run_git("push", "origin", "master:master")
    return sandbox, origin_repo, repo


def create_files(repo_dir: Path, files: List[str]) -> None:
    for relative_path in files:
        file_path = repo_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
