import tempfile

from path import Path

from deveba.gitrepo import GitRepo


def write_file(name, content=""):
    with open(name, "w") as f:
        f.write(content)


def create_repository():
    sandbox = Path(tempfile.mkdtemp(suffix="-unittest"))

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
