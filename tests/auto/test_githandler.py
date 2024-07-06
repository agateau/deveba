# -*- coding: UTF-8 -*-
import os
from pathlib import Path

import pytest

from deveba.userinterface import SilentUserInterface
from deveba.githandler import GitHandler
from tests.auto.utils import write_file, create_repository


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
        old_cwd = os.getcwd()
        self.sandbox, self.origin_repository, self.repository = create_repository(
            tmp_path
        )
        os.chdir(self.repository.path)

        try:
            yield
        finally:
            os.chdir(old_cwd)

    def test_sync(self):
        write_file("new")
        write_file("modified")
        self.repository.add("modified")
        self.repository.commit("commit")
        write_file("modified", "foo")

        diff = self.repository.run_git("diff")

        status = self.repository.get_status()
        assert status.modified_files == ["modified"]
        assert status.new_files == ["new"]

        handler = GitHandler(self.repository.path)
        ui = FakeUserInterface()
        ui.add_question_answer("Show Diff")
        ui.add_question_answer("Commit")
        handler.sync(ui)

        status = self.repository.get_status()
        assert not status.has_changes()

        assert (
            ui.log_verbose_calls.pop(0)
            == "Modified files:\n- modified\n\nNew files:\n- new\n"
        )
        assert ui.log_verbose_calls.pop(0) == diff
