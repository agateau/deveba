import os
from pathlib import Path

import pytest

from deveba.gitrepo import GitRepo
from deveba.handler import HandlerConflictError
from tests.auto.utils import write_file, create_repository


class TestGitRepo:
    @pytest.fixture(autouse=True)
    def setup_sandbox(self, tmp_path: Path):
        old_cwd = os.getcwd()
        self.sandbox, self.origin_repository, self.repository = create_repository(
            tmp_path
        )
        os.chdir(self.repository.path)
        try:
            yield
        finally:
            os.chdir(old_cwd)

    def test_get_status(self):
        write_file("modified")
        self.repository.add("modified")
        new_file1 = "new"
        new_file2 = "néè"
        write_file(new_file1)
        write_file(new_file2)

        status = self.repository.get_status()
        assert status.has_changes()
        assert status.modified_files == ["modified"]
        assert status.new_files == [new_file1, new_file2]

    def test_merge_conflict(self):
        # Create a file and push it
        conflict = "conflict"
        write_file(conflict, "Foo")
        self.repository.add(conflict)
        self.repository.commit("msg")
        self.repository.run_git("push", "origin", "master:master")

        # Clone the repository and modify 'conflict'
        repo2_path = self.sandbox / "repo2"
        repo2 = GitRepo.clone(self.origin_repository.path, repo2_path)
        write_file(repo2_path / "conflict", "Repo2")
        repo2.add(conflict)
        repo2.commit("msg")

        # Push to remote repository
        repo2.run_git("push", "origin", "master:master")

        # Modify 'conflict' in self.repository
        write_file(conflict, "Local")
        self.repository.add(conflict)
        self.repository.commit("msg2")

        # Try to merge
        self.repository.run_git("fetch")
        with pytest.raises(HandlerConflictError) as cm:
            self.repository.merge("origin/master")
        assert cm.value.conflicting_files == ["conflict"]

    def test_need_push(self):
        assert not self.repository.need_push()
        write_file("new")
        self.repository.add("new")
        self.repository.commit("msg")
        assert self.repository.need_push()

    def test_need_merge(self):
        assert not self.repository.need_merge()
        other_repo_path = self.sandbox / "other_repo"
        other_repo = GitRepo.clone(self.origin_repository.path, other_repo_path)
        write_file(other_repo.path / "new_from_other_repo")
        other_repo.add("new_from_other_repo")
        other_repo.commit("commit from other repo")
        other_repo.run_git("push", "origin", "master:master")

        self.repository.run_git("fetch")
        assert self.repository.need_merge()
