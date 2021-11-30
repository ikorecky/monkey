from json import dumps
from pathlib import Path

import pytest

import monkey_island.cc.setup.config_setup  # noqa: F401
from monkey_island.cc.arg_parser import IslandCmdArgs
from monkey_island.cc.server_setup import _extract_config
from monkey_island.cc.server_utils.file_utils import is_windows_os
from monkey_island.cc.setup.island_config_options import IslandConfigOptions

BAD_JSON = '{"data_dir": "C:\\test\\test"'


@pytest.fixture
def cmd_server_config_path(tmpdir) -> Path:
    # Represents the config that user can provide via cmd arguments
    return tmpdir / "fake_server_config.json"


@pytest.fixture
def deployment_server_config_path(tmpdir) -> Path:
    # Represents the config that is built in, deployment specific
    return tmpdir / "fake_server_config3.json"


def create_server_config(config_contents: str, server_config_path: Path):
    with open(server_config_path, "w") as file:
        file.write(config_contents)


@pytest.fixture(autouse=True)
def mock_deployment_config_path(monkeypatch, deployment_server_config_path):
    monkeypatch.setattr(
        "monkey_island.cc.setup.config_setup.PACKAGE_CONFIG_PATH",
        deployment_server_config_path,
    )


def test_extract_config_defaults():
    expected = IslandConfigOptions({})
    assert (
        expected.__dict__
        == _extract_config(IslandCmdArgs(setup_only=False, server_config_path=None)).__dict__
    )


def test_deployment_config_overrides_defaults(deployment_server_config_path):
    expected = IslandConfigOptions({"log_level": "/log_level_2"})
    create_server_config(dumps({"log_level": "/log_level_2"}), deployment_server_config_path)
    assert (
        expected.__dict__
        == _extract_config(IslandCmdArgs(setup_only=False, server_config_path=None)).__dict__
    )


def test_cmd_config_overrides_everything(deployment_server_config_path, cmd_server_config_path):
    expected = IslandConfigOptions({"log_level": "/log_level_3"})
    create_server_config(dumps({"log_level": "/log_level_2"}), deployment_server_config_path)
    create_server_config(dumps({"log_level": "/log_level_3"}), cmd_server_config_path)
    extracted_config = _extract_config(
        IslandCmdArgs(setup_only=False, server_config_path=cmd_server_config_path)
    )
    assert expected.__dict__ == extracted_config.__dict__


def test_not_overriding_unspecified_values(deployment_server_config_path, cmd_server_config_path):
    expected = IslandConfigOptions({"log_level": "/log_level_2", "data_dir": "/data_dir1"})
    create_server_config(dumps({"data_dir": "/data_dir1"}), deployment_server_config_path)
    create_server_config(dumps({"log_level": "/log_level_2"}), cmd_server_config_path)
    extracted_config = _extract_config(
        IslandCmdArgs(setup_only=False, server_config_path=cmd_server_config_path)
    )
    assert expected.__dict__ == extracted_config.__dict__


def test_paths_get_expanded(deployment_server_config_path):
    if is_windows_os():
        path = "%temp%/path"
    else:
        path = "$HOME/path"
    create_server_config(dumps({"data_dir": path}), deployment_server_config_path)
    extracted_config = _extract_config(IslandCmdArgs(setup_only=False, server_config_path=None))
    assert not extracted_config.data_dir == path


def test_malformed_json(cmd_server_config_path):
    create_server_config(BAD_JSON, cmd_server_config_path)
    with pytest.raises(SystemExit):
        _extract_config(IslandCmdArgs(setup_only=False, server_config_path=cmd_server_config_path))
