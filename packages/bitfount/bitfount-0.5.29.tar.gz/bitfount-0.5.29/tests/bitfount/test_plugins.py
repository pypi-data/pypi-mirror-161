"""Tests plugin functionality."""

from importlib import import_module, reload
import inspect
from pathlib import Path
import time

from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from _pytest.tmpdir import TempPathFactory
from pytest import fixture
from pytest_mock import MockerFixture

import bitfount
from bitfount.runners.config_schemas import PodConfig, PodDataConfig
from bitfount.runners.pod_runner import setup_pod_from_config
from tests.utils.helper import unit_test

BITFOUNT_DATA_MODULE_PATH = "bitfount.data"
BITFOUNT_DATASOURCES_MODULE_PATH = f"{BITFOUNT_DATA_MODULE_PATH}.datasources"
DUMMY_MODULE_NAME = "dummy_module"
DUMMY_SOURCE_NAME = "DummySource"


@unit_test
class TestPlugins:
    """Unified class for testing all plugin functionality."""

    @fixture(autouse=True)
    def patch_plugins_dir(
        self, monkeypatch: MonkeyPatch, tmp_path_factory: TempPathFactory
    ) -> None:
        """Monkeypatch `BITFOUNT_PLUGIN_PATH` in bitfount.config to temporary directory.

        We must do it this way instead of by monkeypatching the `BITFOUNT_HOME`
        environment variable to avoid having to reload the `bitfount.config` module as
        this causes issues with the cache of the `_get_environment` function.
        """
        tmpdir = str(tmp_path_factory.mktemp("temp", numbered=True))
        monkeypatch.setattr(
            "bitfount.config.BITFOUNT_PLUGIN_PATH",
            Path(tmpdir) / ".bitfount/_plugins",
        )

    @fixture(scope="function")
    def plugin_suffix(self) -> str:
        """Generates a unique suffix for each plugin in this test run."""
        return str(int(time.time_ns()))  # unix nanosecond timestamp

    @fixture(scope="function")
    def dummy_module_name(self, plugin_suffix: str) -> str:
        """Generates a unique plugin module name for each plugin in this test run."""
        return f"{DUMMY_MODULE_NAME}_{plugin_suffix}"

    @fixture(scope="function")
    def dummy_source_plugin_name(self, plugin_suffix: str) -> str:
        """Generates a unique plugin source name for each plugin in this test run."""
        return f"{DUMMY_SOURCE_NAME}_{plugin_suffix}"

    @fixture(scope="function")
    def dummy_plugin(self, dummy_source_plugin_name: str) -> str:
        """Returns a dummy plugin class."""
        return inspect.cleandoc(
            f"""
        import os
        from typing import Any, Dict, Iterable, List, Optional, Union

        import numpy as np
        import pandas as pd
        from pydantic import AnyUrl

        from bitfount.data.datasources.base_source import BaseSource
        from bitfount.types import _Dtypes

        class {dummy_source_plugin_name}:

            def __init__(
                self,
                path: Union[os.PathLike, AnyUrl, str],
                read_excel_kwargs: Optional[Dict[str, Any]] = None,
                **kwargs: Any,
            ):
                ...

            def get_data(self, **kwargs: Any) -> pd.DataFrame:
                ...

            def get_values(
                self, col_names: List[str], **kwargs: Any
            ) -> Dict[str, Iterable[Any]]:
                ...

            def get_column(
                self, col_name: str, **kwargs: Any
            ) -> Union[np.ndarray, pd.Series]:
                ...

            def get_dtypes(self, **kwargs: Any) -> _Dtypes:
                ...

            def __len__(self) -> int:
                ...

            @property
            def multitable(self) -> bool: # intentional misspelling
                ...
        """
        )

    @fixture(scope="function")
    def dummy_abstract_source_plugin(
        self, dummy_plugin: str, dummy_source_plugin_name: str
    ) -> str:
        """Returns a class that subclasses but doesn't fully implement BaseSource."""
        return dummy_plugin.replace(
            dummy_source_plugin_name, f"{dummy_source_plugin_name}(BaseSource)"
        )

    @fixture(scope="function")
    def dummy_source_plugin(self, dummy_abstract_source_plugin: str) -> str:
        """Returns a class that fully implements BaseSource."""
        return dummy_abstract_source_plugin.replace("multitable", "multi_table")

    def test_no_plugins_dir_created(self) -> None:
        """Tests that the plugin directory is created if it doesn't exist.

        Also tests that it's okay for there to be no plugins within the directory.
        """
        assert bitfount.config.BITFOUNT_PLUGIN_PATH.exists() is False
        reload(bitfount.data.datasources)
        assert bitfount.config.BITFOUNT_PLUGIN_PATH.exists() is True

    def test_plugin_in_wrong_dir_gets_ignored(
        self, dummy_module_name: str, dummy_source_plugin: str
    ) -> None:
        """Tests that plugins in the wrong directory are ignored."""
        reload(bitfount.data.datasources)  # Creates the plugin directory
        # `data_sources` is intentionally the wrong directory, should be `datasources`
        dummy_plugin_path = bitfount.config.BITFOUNT_PLUGIN_PATH / "data_sources"
        dummy_plugin_path.mkdir()
        (dummy_plugin_path / f"{dummy_module_name}.py").touch()
        (dummy_plugin_path / f"{dummy_module_name}.py").write_text(dummy_source_plugin)
        reload(bitfount.data)
        reload(bitfount.data.datasources)
        datasources = import_module("bitfount.data.datasources")
        assert not hasattr(datasources, dummy_module_name)

    def test_datasource_plugin_that_doesnt_subclass_base_source_gets_ignored(
        self, dummy_module_name: str, dummy_plugin: str, dummy_source_plugin_name: str
    ) -> None:
        """Tests that plugins that don't subclass BaseSource are ignored."""
        reload(bitfount.data.datasources)  # Creates the plugin directory
        dummy_plugin_path = bitfount.config.BITFOUNT_PLUGIN_PATH / "datasources"
        (dummy_plugin_path / f"{dummy_module_name}.py").touch()
        (dummy_plugin_path / f"{dummy_module_name}.py").write_text(dummy_plugin)
        reload(bitfount.data)
        reload(bitfount.data.datasources)

        # Tests that the module is still imported but the class is not
        datasources = import_module(BITFOUNT_DATASOURCES_MODULE_PATH)
        data = import_module(BITFOUNT_DATA_MODULE_PATH)
        assert hasattr(datasources, dummy_module_name)
        assert not hasattr(data, dummy_source_plugin_name)

    def test_datasource_plugin_that_doesnt_implement_base_source_gets_ignored(
        self,
        caplog: LogCaptureFixture,
        dummy_abstract_source_plugin: str,
        dummy_module_name: str,
        dummy_source_plugin_name: str,
    ) -> None:
        """Tests that plugins that don't implement BaseSource are ignored."""
        caplog.set_level("DEBUG")
        reload(bitfount.data.datasources)  # Creates the plugin directory
        dummy_plugin_path = bitfount.config.BITFOUNT_PLUGIN_PATH / "datasources"
        (dummy_plugin_path / f"{dummy_module_name}.py").touch()
        (dummy_plugin_path / f"{dummy_module_name}.py").write_text(
            dummy_abstract_source_plugin
        )
        reload(bitfount.data)
        reload(bitfount.data.datasources)

        # Tests that the module is still imported but the class is not
        datasources = import_module(BITFOUNT_DATASOURCES_MODULE_PATH)
        data = import_module(BITFOUNT_DATA_MODULE_PATH)
        assert hasattr(datasources, dummy_module_name)
        assert not hasattr(data, dummy_source_plugin_name)

        # Tests that the appropriate debug message is logged
        assert caplog.records[0].levelname == "DEBUG"
        assert caplog.records[0].message == (
            f"Found class {dummy_source_plugin_name} in module {dummy_module_name} which did not fully implement BaseSource. "  # noqa: B950
            "Skipping."
        )

    def test_datasource_plugin_gets_loaded_via_api(
        self,
        dummy_module_name: str,
        dummy_source_plugin: str,
        dummy_source_plugin_name: str,
    ) -> None:
        """Tests that plugins that implement BaseSource are loaded via the API."""
        reload(bitfount.data.datasources)  # Creates the plugin directory
        dummy_plugin_path = bitfount.config.BITFOUNT_PLUGIN_PATH / "datasources"
        (dummy_plugin_path / f"{dummy_module_name}.py").touch()
        (dummy_plugin_path / f"{dummy_module_name}.py").write_text(dummy_source_plugin)
        reload(bitfount.data.datasources)
        reload(bitfount.data)

        # Tests that the module and class can both be imported
        datasources = import_module(BITFOUNT_DATASOURCES_MODULE_PATH)
        data = import_module(BITFOUNT_DATA_MODULE_PATH)
        assert hasattr(datasources, dummy_module_name)
        assert hasattr(data, dummy_source_plugin_name)

    def test_datasource_plugin_gets_loaded_via_yaml(
        self,
        dummy_module_name: str,
        dummy_source_plugin: str,
        dummy_source_plugin_name: str,
        mocker: MockerFixture,
    ) -> None:
        """Tests that plugins that implement BaseSource are loaded via YAML."""
        reload(bitfount.data.datasources)  # Creates the plugin directory
        dummy_plugin_path = bitfount.config.BITFOUNT_PLUGIN_PATH / "datasources"
        (dummy_plugin_path / f"{dummy_module_name}.py").touch()
        (dummy_plugin_path / f"{dummy_module_name}.py").write_text(dummy_source_plugin)
        reload(bitfount.data)
        reload(bitfount.data.datasources)

        mocker.patch("bitfount.runners.pod_runner._create_bitfounthub")
        mocker.patch("bitfount.runners.pod_runner._create_access_manager")
        mocker.patch("bitfount.runners.pod_runner._get_pod_keys")
        mock_pod = mocker.patch("bitfount.runners.pod_runner.Pod")

        # Sets up the YAML config
        pod_config = PodConfig(
            datasource=dummy_source_plugin_name,
            pod_name="dummy_pod",
            data_config=PodDataConfig(datasource_args={"path": "dummy_module.csv"}),
        )

        # Creates the pod
        setup_pod_from_config(pod_config)

        # Checks that the pod was created
        mock_pod.assert_called_once()

        # Checks that the pod was created with the correct datasource argument
        assert (
            mock_pod.call_args.kwargs["datasource"].__class__.__name__
            == dummy_source_plugin_name
        )
