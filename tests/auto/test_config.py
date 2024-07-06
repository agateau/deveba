from pathlib import Path
from typing import List

from deveba.config import Config
from deveba.group import Group
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


def get_handlers(group: Group) -> List[FakeHandler]:
    """Helper function to return the handlers of a group as a list of FakeHandler
    instead of a list of Handler"""
    lst: List[FakeHandler] = []
    for handler in group.handlers:
        assert isinstance(handler, FakeHandler)
        lst.append(handler)
    return lst


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
    handlers = get_handlers(group)
    assert [x.path for x in handlers] == [Path("/daily1"), Path("/daily2")]

    group = config.groups["manual"]
    handlers = get_handlers(group)
    home_path = Path("~/manual").expanduser()
    opt_path = Path("/opt")
    assert [x.path for x in handlers] == [home_path, opt_path]

    # Check opt_path
    assert handlers[1].options == {"opt1": "foo", "opt2": "bar"}
