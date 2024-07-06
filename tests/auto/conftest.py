import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def git_env_setup():
    author_name = "DevebaTests"
    author_email = "deveba@example.com"

    # We do not use monkeypatch.setenv() because it does not work on session
    # fixtures
    os.environ["GIT_CONFIG_SYSTEM"] = "/dev/null"
    os.environ["GIT_CONFIG_GLOBAL"] = "/dev/null"
    os.environ["GIT_AUTHOR_NAME"] = author_name
    os.environ["GIT_AUTHOR_EMAIL"] = author_email
    os.environ["GIT_COMMITTER_NAME"] = author_name
    os.environ["GIT_COMMITTER_EMAIL"] = author_email
