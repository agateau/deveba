# -*- coding: UTF-8 -*-
import os
import tempfile
import unittest

from path import path

from githandler import GitRepo, GitHandler

def create_file(name):
    path(name).touch()

def create_repository():
    sandbox = path(tempfile.mkdtemp(suffix="-unittest"))

    origin_repo_path = sandbox / "repo.git"
    origin_repo_path.mkdir()
    origin_repo = GitRepo(origin_repo_path)
    origin_repo.run_git("init", "--bare")

    repo = GitRepo.clone(origin_repo.path, sandbox / "repo", "--no-hardlinks")
    create_file(repo.path / "dummy")
    repo.add("dummy")
    repo.commit("created")
    repo.run_git("push", "origin", "master:master")
    return sandbox, origin_repo, repo

class GitHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.old_cwd = os.getcwd()
        self.sandbox, self.origin_repository, self.repository = create_repository()
        os.chdir(self.repository.path)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.sandbox.rmtree()

    def test_get_status(self):
        create_file("modified")
        self.repository.add("modified")
        new_file1 = "new"
        new_file2 = "néè"
        create_file(new_file1)
        create_file(new_file2)

        changes, new_files = self.repository.get_status()
        self.assert_(changes)
        self.assertEqual(new_files, [new_file1, new_file2])

    def test_need_push(self):
        self.assert_(not self.repository.need_push())
        create_file("new")
        self.repository.add("new")
        self.repository.commit("msg")
        self.assert_(self.repository.need_push())

    def test_need_merge(self):
        self.assert_(not self.repository.need_merge())
        other_repo_path = self.sandbox / "other_repo"
        other_repo = GitRepo.clone(self.origin_repository.path, other_repo_path)
        create_file(other_repo.path / "new_from_other_repo")
        other_repo.add("new_from_other_repo")
        other_repo.commit("commit from other repo")
        other_repo.run_git("push", "origin", "master:master")

        self.repository.run_git("fetch")
        self.assert_(self.repository.need_merge())
