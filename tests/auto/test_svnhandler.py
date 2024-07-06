# -*- coding: UTF-8 -*-
import shutil
from subprocess import run

from pathlib import Path

from deveba.svnhandler import SvnHandler
from deveba.userinterface import UserInterface
from tests.auto.utils import create_files


def create_remote_repo(repo_dir):
    repo_dir.mkdir()
    run(["svnadmin", "create", repo_dir])


def checkout(remote_repo_dir, local_repo_dir):
    run(["svn", "checkout", f"file://{remote_repo_dir}", local_repo_dir])


def create_test_setup(base_dir: Path, files=None):
    remote_repo_dir = base_dir / "remote"
    create_remote_repo(remote_repo_dir)

    local_repo_dir = base_dir / "_local"
    checkout(remote_repo_dir, local_repo_dir)
    if files:
        create_files(local_repo_dir, files)
        run_svn_handler(local_repo_dir)
    return remote_repo_dir, local_repo_dir


def run_svn_handler(repo_dir):
    ui = UserInterface()
    handler = SvnHandler.create(repo_dir, options=None)
    assert handler
    handler.sync(ui)


def test_new_file(tmp_path: Path):
    remote_repo_dir, local_repo_dir = create_test_setup(tmp_path)

    handler = SvnHandler.create(local_repo_dir, options=None)
    assert handler

    (local_repo_dir / "foo").touch()

    run_svn_handler(local_repo_dir)


def test_update(tmp_path: Path):
    remote_repo_dir, local_repo1_dir = create_test_setup(tmp_path)

    # Create a second checkout, add files
    local_repo2_dir = tmp_path / "local2"
    checkout(remote_repo_dir, local_repo2_dir)
    create_files(local_repo2_dir, ["foo", "bar/baz"])
    run_svn_handler(local_repo2_dir)

    # Update first checkout
    run_svn_handler(local_repo1_dir)

    # First checkout must contain new files
    assert (local_repo1_dir / "foo").exists()
    assert (local_repo1_dir / "bar/baz").exists()


def test_remove(tmp_path: Path):
    remote_repo_dir, local_repo1_dir = create_test_setup(
        tmp_path, ["foo", "dir1/bar", "dir2/baz"]
    )
    # Create a repository with a file in it

    # Checkout the repository
    local_repo2_dir = tmp_path / "local2"
    checkout(remote_repo_dir, local_repo2_dir)

    # Rm files from local2
    (local_repo2_dir / "foo").unlink()
    shutil.rmtree(local_repo2_dir / "dir1")

    # Sync local2
    run_svn_handler(local_repo2_dir)

    # Sync local1, the file should be gone
    run_svn_handler(local_repo1_dir)
    assert not (local_repo1_dir / "foo").exists()
    assert not (local_repo1_dir / "dir1").exists()
