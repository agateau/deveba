# -*- coding: UTF-8 -*-
import os
import tempfile
import unittest

from path import Path

from deveba.userinterface import SilentUserInterface
from deveba.handler import HandlerConflictError
from deveba.githandler import GitRepo, GitHandler

def write_file(name, content=""):
    with open(name, "wt") as f:
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


class TestUserInterface(SilentUserInterface):
    def __init__(self):
        self.log_verbose_calls = []
        self.question_answers = []

    def add_question_answer(self, answer):
        self.question_answers.append(answer)

    def log_verbose(self, text):
        self.log_verbose_calls.append(text)

    def question(self, msg, choices, default):
        return self.question_answers.pop(0)


class GitHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.old_cwd = os.getcwd()
        self.sandbox, self.origin_repository, self.repository = create_repository()
        os.chdir(self.repository.path)

    def create_test_handler(self):
        return GitHandler(self.repository.path)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.sandbox.rmtree()

    def test_sync(self):
        write_file("new")
        write_file("modified")
        self.repository.add("modified")
        self.repository.commit("commit")
        write_file("modified", "foo")

        diff = self.repository.run_git("diff")

        status = self.repository.get_status()
        self.assertEqual(status.modified_files, ["modified"])
        self.assertEqual(status.new_files, ["new"])

        handler = self.create_test_handler()
        ui = TestUserInterface()
        ui.add_question_answer("Show Diff")
        ui.add_question_answer("Commit")
        handler.sync(ui)

        status = self.repository.get_status()
        self.assertTrue(not status.has_changes())

        self.assertEqual(ui.log_verbose_calls.pop(0), "Modified files:\n- modified\n\nNew files:\n- new\n")
        self.assertEqual(ui.log_verbose_calls.pop(0), diff)

