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


class SvnTestCase(unittest.TestCase):
    def test_new_file(self):
        with TemporaryDirectory() as tmpdirname:
            remote_repo_dir = Path(tmpdirname) / "remote"
            create_remote_repo(remote_repo_dir)

            local_repo_dir = Path(tmpdirname) / "local"
            checkout(remote_repo_dir, local_repo_dir)

            handler = SvnHandler.create(local_repo_dir, options=None)
            self.assertIsNotNone(handler)

            write_file(local_repo_dir / "foo")

            ui = UserInterface()
            handler.sync(ui)

    def test_update(self):
        with TemporaryDirectory() as tmpdirname:
            ui = UserInterface()
            remote_repo_dir = Path(tmpdirname) / "remote"
            create_remote_repo(remote_repo_dir)

            # Create a first checkout
            local_repo1_dir = Path(tmpdirname) / "local1"
            checkout(remote_repo_dir, local_repo1_dir)

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
