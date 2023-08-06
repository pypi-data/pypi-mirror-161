import shutil
from pathlib import Path

import multivenv
from multivenv import _platform
from multivenv._config import TargetConfig
from tests.config import (
    BASIC_REQUIREMENTS_HASH,
    REQUIREMENTS_IN_PATH,
    REQUIREMENTS_OUT_PATH,
)
from tests.dirutils import change_directory_to
from tests.fixtures.temp_dir import temp_dir


def test_info(temp_dir: Path):
    shutil.copy(REQUIREMENTS_IN_PATH, temp_dir)
    shutil.copy(REQUIREMENTS_OUT_PATH, temp_dir)
    venvs: multivenv.Venvs = {"basic": None}
    with change_directory_to(temp_dir):
        multivenv.sync(venvs=venvs)
        all_info = multivenv.info(["basic"], venvs=venvs)
        assert len(all_info) == 1
        current_target = TargetConfig.from_system()
        assert all_info.system.version == current_target.version
        assert all_info.system.platform == current_target.platform
        info = all_info[0]
        assert info.name == "basic"
        assert info.path == Path("venvs", "basic")
        assert info.config_requirements.in_path == Path("requirements.in")
        assert info.config_requirements.out_path == Path("requirements.txt")
        assert info.discovered_requirements.in_path == Path("requirements.in")
        assert info.discovered_requirements.out_path == Path("requirements.txt")
        assert info.exists is True
        assert info.state.needs_sync is False
        assert info.state.requirements_hash == BASIC_REQUIREMENTS_HASH
