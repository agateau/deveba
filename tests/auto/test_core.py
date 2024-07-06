from pathlib import Path

from deveba.core import load_config
from deveba.githandler import GitHandler


def test_load_config(tmp_path: Path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    # Create a .git dir to please GitHandler
    (repo_path / ".git").mkdir()

    config_path = tmp_path / "config.xml"
    config_path.write_text(f"""
<config>
    <group name="g1">
        <repo path="{repo_path}"/>
    </group>
</config>
""")

    config = load_config(config_path)

    assert len(config.groups) == 1
    g1 = config.groups["g1"]

    assert len(g1.handlers) == 1
    handler = g1.handlers[0]

    assert isinstance(handler, GitHandler)
    assert Path(handler.repo.path) == repo_path
