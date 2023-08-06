"""Modules for data sources.

Datasource plugins can also be imported from this package.
"""
import logging as _logging
import pkgutil as _pkgutil

from bitfount.config import BITFOUNT_PLUGIN_PATH as _BITFOUNT_PLUGIN_PATH
from bitfount.utils import _get_module_from_file

_logger = _logging.getLogger(__name__)

# Create `datasources` plugin subdir if it doesn't exist
_datasource_plugin_path = _BITFOUNT_PLUGIN_PATH / "datasources"
_datasource_plugin_path.mkdir(parents=True, exist_ok=True)

# Add datasource plugin modules to the `datasources` namespace alongside the existing
# built-in datasource modules. This is not essential, but it allows users to import
# the entire plugin module as opposed to just the Datasource class which is what is done
# in the `bitfount.data` __init__ module.
for _module_info in _pkgutil.walk_packages(
    [str(_datasource_plugin_path)],
):
    try:
        _module = _get_module_from_file(
            _datasource_plugin_path / f"{_module_info.name}.py"
        )
        globals().update({_module.__name__: _module})
        _logger.info(f"Loaded datasource plugin: {_module_info.name}")
    except ImportError:
        pass
