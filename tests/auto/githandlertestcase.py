# -*- coding: UTF-8 -*-
import os
import unittest

from deveba.userinterface import SilentUserInterface
from deveba.githandler import GitHandler
from tests.auto.utils import write_file, create_repository


class FakeUserInterface(SilentUserInterface):
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
        ui = FakeUserInterface()
        ui.add_question_answer("Show Diff")
        ui.add_question_answer("Commit")
        handler.sync(ui)

        status = self.repository.get_status()
        self.assertTrue(not status.has_changes())

        self.assertEqual(
            ui.log_verbose_calls.pop(0),
            "Modified files:\n- modified\n\nNew files:\n- new\n",
        )
        self.assertEqual(ui.log_verbose_calls.pop(0), diff)
