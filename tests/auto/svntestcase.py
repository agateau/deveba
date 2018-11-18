# -*- coding: UTF-8 -*-
import unittest
from subprocess import run
from tempfile import TemporaryDirectory

from path import Path

from deveba.svnhandler import SvnHandler
from deveba.userinterface import UserInterface


def write_file(name, content=""):
    with open(name, "wt") as f:
        f.write(content)


def create_remote_repo(repo_dir):
    Path(repo_dir).mkdir()
    run(["svnadmin", "create", repo_dir])


def checkout(remote_repo_dir, local_repo_dir):
    run(["svn", "checkout", "file://" + remote_repo_dir, local_repo_dir])


def create_test_setup(base_dir):
    remote_repo_dir = Path(base_dir) / "remote"
    create_remote_repo(remote_repo_dir)

    local_repo_dir = Path(base_dir) / "local"
    checkout(remote_repo_dir, local_repo_dir)
    return remote_repo_dir, local_repo_dir


class SvnTestCase(unittest.TestCase):
    def test_new_file(self):
        with TemporaryDirectory() as tmpdirname:
            remote_repo_dir, local_repo_dir = create_test_setup(tmpdirname)

            handler = SvnHandler.create(local_repo_dir, options=None)
            self.assertIsNotNone(handler)

            write_file(local_repo_dir / "foo")

            ui = UserInterface()
            handler.sync(ui)

    def test_update(self):
        with TemporaryDirectory() as tmpdirname:
            ui = UserInterface()
            remote_repo_dir, local_repo1_dir = create_test_setup(tmpdirname)

            # Create a second checkout, add a file
            local_repo2_dir = Path(tmpdirname) / "local2"
            checkout(remote_repo_dir, local_repo2_dir)
            write_file(local_repo2_dir / "foo")
            handler = SvnHandler.create(local_repo2_dir, options=None)
            handler.sync(ui)

            # Update first checkout
            handler = SvnHandler.create(local_repo1_dir, options=None)
            handler.sync(ui)

            # First checkout must contain new file
            self.assertTrue((local_repo1_dir / "foo").exists())
