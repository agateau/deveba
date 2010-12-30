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
  </group>
</config>
"""

class TestHandler(Handler):
    @classmethod
    def can_handle(self, path):
        return True

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
        self.assert_("/daily1" in group.handlers)
        self.assert_("/daily2" in group.handlers)

        group = config.groups["manual"]
        repo_path = path("~/manual").expanduser()
        self.assertEqual(len(group.handlers), 1)
        self.assert_(repo_path in group.handlers)

        handler = group.handlers[repo_path]
        self.assertEqual(handler.path.__class__, path)
