import os
import unittest

from deveba.gitrepo import GitRepo
from deveba.handler import HandlerConflictError
from tests.auto.utils import write_file, create_repository


class GitRepoTestCase(unittest.TestCase):
    def setUp(self):
        self.old_cwd = os.getcwd()
        self.sandbox, self.origin_repository, self.repository = create_repository()
        os.chdir(self.repository.path)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.sandbox.rmtree()

    def test_get_status(self):
        write_file("modified")
        self.repository.add("modified")
        new_file1 = "new"
        new_file2 = "néè"
        write_file(new_file1)
        write_file(new_file2)

        status = self.repository.get_status()
        self.assertTrue(status.has_changes())
        self.assertEqual(status.modified_files, ["modified"])
        self.assertEqual(status.new_files, [new_file1, new_file2])

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
        with self.assertRaises(HandlerConflictError) as cm:
            self.repository.merge("origin/master")
        exc = cm.exception
        self.assertEqual(exc.conflicting_files, ["conflict"])

    def test_need_push(self):
        self.assertTrue(not self.repository.need_push())
        write_file("new")
        self.repository.add("new")
        self.repository.commit("msg")
        self.assertTrue(self.repository.need_push())

    def test_need_merge(self):
        self.assertTrue(not self.repository.need_merge())
        other_repo_path = self.sandbox / "other_repo"
        other_repo = GitRepo.clone(self.origin_repository.path, other_repo_path)
        write_file(other_repo.path / "new_from_other_repo")
        other_repo.add("new_from_other_repo")
        other_repo.commit("commit from other repo")
        other_repo.run_git("push", "origin", "master:master")

        self.repository.run_git("fetch")
        self.assertTrue(self.repository.need_merge())
