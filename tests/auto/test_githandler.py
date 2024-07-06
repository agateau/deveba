# -*- coding: UTF-8 -*-
from pathlib import Path


from deveba.gitrepo import GitRepo
from deveba.userinterface import SilentUserInterface
from deveba.githandler import GitHandler
from tests.auto.utils import create_repository


class FakeUserInterface(SilentUserInterface):
    def __init__(self):
        self.log_verbose_calls = []
        self.question_answers = []

    def add_question_answer(self, answer):
        self.question_answers.append(answer)

    def log_verbose(self, msg):
        self.log_verbose_calls.append(msg)

    def question(self, msg, choices, default):
        return self.question_answers.pop(0)


def test_sync(tmp_path: Path):
    _, _, repo = create_repository(tmp_path)

    # GIVEN a commit containing the file "modified"
    modified_path = repo.path / "modified"
    modified_path.touch()

    repo.add("modified")
    repo.commit("commit")

    # AND "modified" has been modified after the commit
    modified_path.write_text("foo")

    # AND a file "new" has been created after the commit
    new_path = repo.path / "new"
    new_path.touch()

    # THEN repository.get_status() reports them with their correct status
    status = repo.get_status()
    assert status.modified_files == ["modified"]
    assert status.new_files == ["new"]

    diff = repo.run_git("diff")

    # WHEN syncing the repository
    handler = GitHandler(repo.path)
    ui = FakeUserInterface()
    ui.add_question_answer("Show Diff")
    ui.add_question_answer("Commit")
    handler.sync(ui)

    # THEN repository.get_status() does not report any changes
    status = repo.get_status()
    assert not status.has_changes()

    # AND the log contains a report of the changes
    assert (
        ui.log_verbose_calls.pop(0)
        == "Modified files:\n- modified\n\nNew files:\n- new\n"
    )
    assert ui.log_verbose_calls.pop(0) == diff


def test_merge_upstream_changes(tmp_path: Path):
    # GIVEN a repo and a remote repo
    _, remote_repo, repo = create_repository(tmp_path)

    # AND the remote repo has received new changes
    repo2_new_content = "hello from repo2"
    repo2 = GitRepo.clone(remote_repo.path, tmp_path / "repo2")
    (repo2.path / "new").write_text(repo2_new_content)
    repo2.add("new")
    repo2.commit("changes!")
    repo2.run_git("push")

    # WHEN syncing the repository
    handler = GitHandler(repo.path)
    handler.sync(SilentUserInterface())

    # THEN the new changes are received
    assert (repo.path / "new").read_text() == repo2_new_content


def test_str(tmp_path: Path):
    handler = GitHandler(tmp_path)
    assert isinstance(str(handler), str)
