# -*- coding: UTF-8 -*-
import os
import tempfile
import unittest
from StringIO import StringIO

from path import path

from config import Config

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

class ConfigTestCase(unittest.TestCase):
    def test_parse(self):
        config = Config()
        fp = StringIO(TEST_CONFIG)
        config.parsefp(fp)

        self.assertEqual(len(config.groups), 2)
        self.assert_("daily" in config.groups)
        self.assert_("manual" in config.groups)

        group = config.groups["daily"]
        self.assertEqual(len(group.repositories), 2)
        self.assert_("/daily1" in group.repositories)
        self.assert_("/daily2" in group.repositories)

        group = config.groups["manual"]
        repo_path = path("~/manual").expanduser()
        self.assertEqual(len(group.repositories), 1)
        self.assert_(repo_path in group.repositories)

        repo = group.repositories[repo_path]
        self.assertEqual(repo.path.__class__, path)
