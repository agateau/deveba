# -*- coding: UTF-8 -*-
import os
import tempfile
import unittest

from path import path

from githandler import run_git, get_status, GitHandler

def create_file(name):
    path(name).touch()

def create_repository():
    repo = tempfile.mkdtemp(suffix="-unittest", dir=os.getcwd())
    run_git("init", repo)
    return path(repo).abspath()

class GitHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.old_cwd = os.getcwd()
        self.repository = create_repository()
        os.chdir(self.repository)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.repository.rmtree()

    def test_get_status(self):
        create_file("modified")
        run_git("add", "modified")
        new_file1 = "new"
        new_file2 = "néè"
        create_file(new_file1)
        create_file(new_file2)

        changes, new_files = get_status()
        self.assert_(changes)
        self.assertEqual(new_files, [new_file1, new_file2])
