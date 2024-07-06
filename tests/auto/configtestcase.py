from pathlib import Path

from deveba.config import Config
from deveba.handler import Handler

TEST_CONFIG = """
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


class FakeHandler(Handler):
    def __init__(self, path, options):
        self.path = path
        self.options = options

    @classmethod
    def create(cls, repo_path, options):
        return FakeHandler(repo_path, options)

    def __str__(self):
        return self.path


def test_parse(tmp_path: Path):
    config_path = tmp_path / "config"
    config_path.write_text(TEST_CONFIG)

    config = Config()
    config.add_handler_class(FakeHandler)
    config.parse(config_path)

    assert len(config.groups) == 2
    assert "daily" in config.groups
    assert "manual" in config.groups

    group = config.groups["daily"]
    assert len(group.handlers) == 2
    assert group.handlers[0].path == "/daily1"
    assert group.handlers[1].path == "/daily2"

    group = config.groups["manual"]
    home_path = Path("~/manual").expanduser()
    opt_path = Path("/opt")
    assert len(group.handlers) == 2
    assert Path(group.handlers[0].path) == home_path
    assert Path(group.handlers[1].path) == opt_path

    # Check opt_path
    assert group.handlers[1].options == {"opt1": "foo", "opt2": "bar"}
