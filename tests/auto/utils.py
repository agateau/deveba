from pathlib import Path
from typing import List

from deveba.gitrepo import GitRepo


def create_repository(sandbox: Path):
    origin_repo_path = sandbox / "repo.git"
    origin_repo_path.mkdir()
    origin_repo = GitRepo(origin_repo_path)
    origin_repo.run_git("init", "--bare")

    repo = GitRepo.clone(origin_repo.path, sandbox / "repo", "--no-hardlinks")
    (repo.path / "dummy").touch()
    repo.add("dummy")
    repo.commit("created")
    repo.run_git("push", "origin", "master:master")
    return sandbox, origin_repo, repo


def create_files(base_dir: Path, files: List[str]) -> None:
    for relative_path in files:
        file_path = base_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
