# -*- coding: UTF-8 -*-
from pathlib import Path

import pytest

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


class TestGitHandler:
    @pytest.fixture(autouse=True)
    def setup_sandbox(self, tmp_path: Path):
        _, _, self.repository = create_repository(tmp_path)

    def test_sync(self):
        # GIVEN a commit containing the file "modified"
        modified_path = self.repository.path / "modified"
        modified_path.touch()

        self.repository.add("modified")
        self.repository.commit("commit")

        # AND "modified" has been modified after the commit
        modified_path.write_text("foo")

        # AND a file "new" has been created after the commit
        new_path = self.repository.path / "new"
        new_path.touch()

        # THEN repository.get_status() reports them with their correct status
        status = self.repository.get_status()
        assert status.modified_files == ["modified"]
        assert status.new_files == ["new"]

        diff = self.repository.run_git("diff")

        # WHEN syncing the repository
        handler = GitHandler(self.repository.path)
        ui = FakeUserInterface()
        ui.add_question_answer("Show Diff")
        ui.add_question_answer("Commit")
        handler.sync(ui)

        # THEN repository.get_status() does not report any changes
        status = self.repository.get_status()
        assert not status.has_changes()

        # AND the log contains a report of the changes
        assert (
            ui.log_verbose_calls.pop(0)
            == "Modified files:\n- modified\n\nNew files:\n- new\n"
        )
        assert ui.log_verbose_calls.pop(0) == diff

    def test_str(self):
        handler = GitHandler(self.repository.path)
        assert isinstance(str(handler), str)
