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
        home_path = path("~/manual").expanduser()
        opt_path = "/opt"
        self.assertEqual(len(group.handlers), 2)
        self.assert_(home_path in group.handlers)
        self.assert_(opt_path in group.handlers)

        # Check home_path
        handler = group.handlers[home_path]
        self.assertEqual(handler.path.__class__, path)

        # Check opt_path
        handler = group.handlers[opt_path]
        self.assertEqual(handler.options, {"opt1":"foo", "opt2":"bar"})
