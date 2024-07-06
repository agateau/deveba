from pathlib import Path

from deveba.core import load_config
from deveba.userinterface import UserInterface
from tests.auto.utils import create_files


def test_rsync_handler(tmp_path: Path):
    # GIVEN a source dir with some files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    source_files = ["foo", "bar/baz"]
    create_files(src_dir, source_files)

    # AND a destination dir
    dst_dir = tmp_path / "dst"
    dst_dir.mkdir()

    # AND a deveba config with an rsync repo connecting the dirs
    config_path = tmp_path / "config"
    config_path.write_text(f"""
<config>
    <group name="g">
        <repo type="rsync" path="{src_dir}" destination="{dst_dir}"/>
    </group>
</config>
""")

    config = load_config(config_path)
    handler = config.groups["g"].handlers[0]
    assert handler

    # WHEN the handler is run
    ui = UserInterface()
    handler.sync(ui)

    # THEN the destination dir contains the source dir files
    for name in source_files:
        assert (dst_dir / name).exists()
