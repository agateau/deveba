#!/usr/bin/env python3
# ruff: noqa: F401
import os
import unittest

from githandlertestcase import GitRepoTestCase, GitHandlerTestCase
from configtestcase import ConfigTestCase
from svntestcase import SvnTestCase


def git_env_setup():
    os.environ["GIT_CONFIG_SYSTEM"] = "/dev/null"
    os.environ["GIT_CONFIG_GLOBAL"] = "/dev/null"
    os.environ["GIT_AUTHOR_NAME"] = "DevebaTests"
    os.environ["GIT_AUTHOR_EMAIL"] = "deveba@example.com"

    os.environ["GIT_COMMITTER_NAME"] = os.environ["GIT_AUTHOR_NAME"]
    os.environ["GIT_COMMITTER_EMAIL"] = os.environ["GIT_AUTHOR_EMAIL"]


def main():
    git_env_setup()
    unittest.main()


if __name__ == "__main__":
    main()
# vi: ts=4 sw=4 et
