from pathlib import Path

from deveba.core import load_config
from deveba.userinterface import UserInterface
from tests.auto.utils import create_files


def test_unison_handler(tmp_path: Path, monkeypatch):
    # GIVEN dir1 with some files
    dir1 = tmp_path / "src"
    dir1_files = ["foo1", "bar/baz1"]
    create_files(dir1, dir1_files)

    # AND dir2 with other files
    dir2 = tmp_path / "dst"
    dir2_files = ["foo2", "bar/baz2"]
    create_files(dir2, dir2_files)

    # AND a Unison profile
    unison_dir = tmp_path / ".unison"
    monkeypatch.setenv("UNISON", str(unison_dir))
    unison_dir.mkdir()
    (unison_dir / "profile.prf").write_text(
        f"""
root = {dir1}
root = {dir2}
        """
    )

    # AND a deveba config with an unison repo connecting the dirs
    config_path = tmp_path / "config"
    config_path.write_text("""
<config>
    <group name="g">
        <repo type="unison" path="profile" />
    </group>
</config>
""")

    config = load_config(config_path)
    handler = config.groups["g"].handlers[0]
    assert handler

    # WHEN the handler is run
    ui = UserInterface()
    handler.sync(ui)

    # THEN the dirs are synced
    for name in dir1_files + dir2_files:
        assert (dir1 / name).exists()
        assert (dir2 / name).exists()
