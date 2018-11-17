# -*- coding: UTF-8 -*-
import os
import tempfile
import unittest
from io import StringIO

from path import Path

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
    def __init__(self, path, options):
        self.path = path
        self.options = options

    @classmethod
    def create(self, path, options):
        return TestHandler(path, options)

    def __str__(self):
        return self.path


class ConfigTestCase(unittest.TestCase):
    def test_parse(self):
        config = Config()
        config.add_handler_class(TestHandler)
        fp = StringIO(TEST_CONFIG)
        config.parsefp(fp)

        self.assertEqual(len(config.groups), 2)
        self.assertTrue("daily" in config.groups)
        self.assertTrue("manual" in config.groups)

        group = config.groups["daily"]
        self.assertEqual(len(group.handlers), 2)
        self.assertEqual(group.handlers[0].path, "/daily1")
        self.assertEqual(group.handlers[1].path, "/daily2")

        group = config.groups["manual"]
        home_path = Path("~/manual").expanduser()
        opt_path = "/opt"
        self.assertEqual(len(group.handlers), 2)
        self.assertEqual(group.handlers[0].path, home_path)
        self.assertEqual(group.handlers[1].path, opt_path)

        # Check opt_path
        self.assertEqual(group.handlers[1].options, {"opt1":"foo", "opt2":"bar"})
