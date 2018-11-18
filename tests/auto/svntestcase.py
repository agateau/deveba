# -*- coding: UTF-8 -*-
import unittest
from subprocess import run
from tempfile import TemporaryDirectory

from path import Path

from deveba.svnhandler import SvnHandler
from deveba.userinterface import UserInterface


def create_remote_repo(repo_dir):
    Path(repo_dir).mkdir()
    run(["svnadmin", "create", repo_dir])


def checkout(remote_repo_dir, local_repo_dir):
    run(["svn", "checkout", "file://" + remote_repo_dir, local_repo_dir])


def create_files(repo_dir, files):
    for relative_path in files:
        file_path = repo_dir / relative_path
        file_path.dirname().makedirs_p()
        file_path.touch()


def create_test_setup(base_dir, files=None):
    remote_repo_dir = Path(base_dir) / "remote"
    create_remote_repo(remote_repo_dir)

    local_repo_dir = Path(base_dir) / "_local"
    checkout(remote_repo_dir, local_repo_dir)
    if files:
        create_files(local_repo_dir, files)
        run_svn_handler(local_repo_dir)
    return remote_repo_dir, local_repo_dir


def run_svn_handler(repo_dir):
    ui = UserInterface()
    handler = SvnHandler.create(repo_dir, options=None)
    handler.sync(ui)


class SvnTestCase(unittest.TestCase):
    def test_new_file(self):
        with TemporaryDirectory() as tmpdirname:
            remote_repo_dir, local_repo_dir = create_test_setup(tmpdirname)

            handler = SvnHandler.create(local_repo_dir, options=None)
            self.assertIsNotNone(handler)

            (local_repo_dir / "foo").touch()

            run_svn_handler(local_repo_dir)

    def test_update(self):
        with TemporaryDirectory() as tmpdirname:
            remote_repo_dir, local_repo1_dir = create_test_setup(tmpdirname)

            # Create a second checkout, add files
            local_repo2_dir = Path(tmpdirname) / "local2"
            checkout(remote_repo_dir, local_repo2_dir)
            create_files(local_repo2_dir, ["foo", "bar/baz"])
            run_svn_handler(local_repo2_dir)

            # Update first checkout
            run_svn_handler(local_repo1_dir)

            # First checkout must contain new files
            self.assertTrue((local_repo1_dir / "foo").exists())
            self.assertTrue((local_repo1_dir / "bar/baz").exists())

    def test_remove(self):
        with TemporaryDirectory() as tmpdirname:
            # Create a repository with a file in it
            remote_repo_dir, local_repo1_dir = create_test_setup(tmpdirname,
                                                                 ["foo",
                                                                  "dir1/bar",
                                                                  "dir2/baz"])

            # Checkout the repository
            local_repo2_dir = Path(tmpdirname) / "local2"
            checkout(remote_repo_dir, local_repo2_dir)

            # Rm files from local2
            (local_repo2_dir / "foo").remove()
            (local_repo2_dir / "dir1").rmtree()

            # Sync local2
            run_svn_handler(local_repo2_dir)

            # Sync local1, the file should be gone
            run_svn_handler(local_repo1_dir)
            self.assertFalse((local_repo1_dir / "foo").exists())
            self.assertFalse((local_repo1_dir / "dir1").exists())
