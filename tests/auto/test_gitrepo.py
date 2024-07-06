from pathlib import Path

import pytest

from deveba.gitrepo import GitRepo
from deveba.handler import HandlerConflictError
from tests.auto.utils import create_repository, create_files


class TestGitRepo:
    @pytest.fixture(autouse=True)
    def setup_sandbox(self, tmp_path: Path):
        self.sandbox, self.origin_repository, self.repository = create_repository(
            tmp_path
        )

    def test_get_status(self):
        # GIVEN a file added to the index
        modified_file = self.repository.path / "modified"
        modified_file.write_text("modified")
        self.repository.add("modified")

        # AND new files
        new_files = ["new", "néè"]
        create_files(self.repository.path, new_files)

        # WHEN get_status() is called
        status = self.repository.get_status()

        # THEN it reports changes
        assert status.has_changes()

        # AND the status contains the appropriate details
        assert status.modified_files == ["modified"]
        assert status.new_files == new_files

    def test_merge_conflict(self):
        # GIVEN a repository with one file named "conflict"
        conflict_name = "conflict"
        conflict1_path = self.repository.path / conflict_name
        conflict1_path.write_text("Foo")
        self.repository.add(conflict_name)
        self.repository.commit("msg")
        self.repository.run_git("push", "origin", "master:master")

        # AND the file has been modified from another clone of the repository
        repo2_path = self.sandbox / "repo2"
        conflict2_path = repo2_path / conflict_name
        repo2 = GitRepo.clone(self.origin_repository.path, repo2_path)

        conflict2_path.write_text("Repo2")
        repo2.add(conflict_name)
        repo2.commit("msg")
        repo2.run_git("push", "origin", "master:master")

        # AND I modify "conflict"
        conflict1_path.write_text("Local")
        self.repository.add(conflict_name)
        self.repository.commit("msg2")

        # WHEN I try to merge
        self.repository.run_git("fetch")

        # THEN an exception is raised
        with pytest.raises(HandlerConflictError) as cm:
            self.repository.merge("origin/master")

        # AND it lists the conflicting files
        assert cm.value.conflicting_files == [conflict_name]

    def test_need_push(self):
        # GIVEN self.repository does not need a push
        assert not self.repository.need_push()

        # WHEN a new commit is created
        (self.repository.path / "new").touch()
        self.repository.add("new")
        self.repository.commit("msg")

        # THEN self.repository needs a push
        assert self.repository.need_push()

    def test_need_merge(self):
        # GIVEN self.repository does not need a merge
        assert not self.repository.need_merge()

        # AND the remote repository has been updated to contain a new file
        other_repo_path = self.sandbox / "other_repo"
        other_repo = GitRepo.clone(self.origin_repository.path, other_repo_path)

        (other_repo.path / "new_from_other_repo").touch()
        other_repo.add("new_from_other_repo")
        other_repo.commit("commit from other repo")
        other_repo.run_git("push", "origin", "master:master")

        # WHEN self.repository is fetched
        self.repository.run_git("fetch")

        # THEN need_merge() returns True
        assert self.repository.need_merge()
