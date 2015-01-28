# -*- coding: UTF-8 -*-
import os
import tempfile
import unittest
from StringIO import StringIO

from path import path

from config import Config
from handler import Handler

TEST_CONFIG="""
<config>
  <group name="daily">
    <repo path="/daily1"/>
    <repo path="/daily2"/>
  </group>
  <group name="manual">
    <repo path="~/manual"/>
    <repo path="/opt" opt1="foo" opt2="bar"/>
  </group>
</config>
"""

class TestHandler(Handler):
    def __init__(self, path):
        self.path = path

    @classmethod
    def create(self, path):
        return TestHandler(path)

    def __str__(self):
        return self.path


class ConfigTestCase(unittest.TestCase):
    def test_parse(self):
        config = Config()
        config.add_handler_class(TestHandler)
        fp = StringIO(TEST_CONFIG)
        config.parsefp(fp)

        self.assertEqual(len(config.groups), 2)
        self.assert_("daily" in config.groups)
        self.assert_("manual" in config.groups)

        group = config.groups["daily"]
        self.assertEqual(len(group.handlers), 2)
        self.assertEqual(group.handlers[0].path, "/daily1")
        self.assertEqual(group.handlers[1].path, "/daily2")

        group = config.groups["manual"]
        home_path = path("~/manual").expanduser()
        opt_path = "/opt"
        self.assertEqual(len(group.handlers), 2)
        self.assertEqual(group.handlers[0].path, home_path)
        self.assertEqual(group.handlers[1].path, opt_path)

        # Check opt_path
        self.assertEqual(group.handlers[1].options, {"opt1":"foo", "opt2":"bar"})
