"""Modules for handling model data flow.

Data plugins can also be imported from this package.
"""
import importlib as _importlib
import inspect as _inspect
import logging as _logging
import pkgutil as _pkgutil
from typing import List as _List

from bitfount.config import BITFOUNT_PLUGIN_PATH as _BITFOUNT_PLUGIN_PATH
from bitfount.data import datasources as datasources
from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasplitters import PercentageSplitter, SplitterDefinedInData
from bitfount.data.datastructure import DataStructure
from bitfount.data.exceptions import (
    BitfountSchemaError,
    DatabaseMissingTableError,
    DatabaseSchemaNotFoundError,
    DatabaseUnsupportedQueryError,
    DataNotLoadedError,
    DatasetSplitterError,
    DataStructureError,
    DuplicateColumnError,
)
from bitfount.data.helper import convert_epochs_to_steps
from bitfount.data.schema import BitfountSchema, TableSchema
from bitfount.data.types import (
    CategoricalRecord,
    ContinuousRecord,
    DataPathModifiers,
    ImageRecord,
    SemanticType,
    TextRecord,
)
from bitfount.data.utils import DatabaseConnection
from bitfount.utils import _get_module_from_file

_logger = _logging.getLogger(__name__)
__all__: _List[str] = [
    "BitfountSchema",
    "BitfountSchemaError",
    "CategoricalRecord",
    "ContinuousRecord",
    "DatabaseConnection",
    "DatabaseMissingTableError",
    "DatabaseSchemaNotFoundError",
    "DatabaseUnsupportedQueryError",
    "DatasetSplitterError",
    "DataNotLoadedError",
    "DataPathModifiers",
    "DataStructure",
    "DataStructureError",
    "DuplicateColumnError",
    "ImageRecord",
    "PercentageSplitter",
    "SemanticType",
    "SplitterDefinedInData",
    "TableSchema",
    "TextRecord",
    "convert_epochs_to_steps",
]


# Import all concrete implementations of BaseSource in the datasources subdirectory
# as well as datasource plugins
for _module_info in _pkgutil.walk_packages(
    path=datasources.__path__ + [str(_BITFOUNT_PLUGIN_PATH / "datasources")],
):
    try:
        _module = _importlib.import_module(
            f"{datasources.__name__}.{_module_info.name}"
        )
    # Also catches `ModuleNotFoundError` which subclasses `ImportError`
    # Try to import the module from the plugin directory if it's not found in the
    # datasources directory
    except ImportError:
        try:
            _module = _get_module_from_file(
                _BITFOUNT_PLUGIN_PATH / "datasources" / f"{_module_info.name}.py",
            )
        except ImportError:
            _logger.debug(f"Error importing module {_module_info.name}")
    finally:
        for _, cls in _inspect.getmembers(_module, _inspect.isclass):
            if issubclass(cls, BaseSource) and not _inspect.isabstract(cls):
                globals().update({cls.__name__: getattr(_module, cls.__name__)})
                __all__.append(cls.__name__)
            # There are too many false positives if we don't restrict classes to those
            # that inherit from BaseSource for it to be a useful log message
            elif issubclass(cls, BaseSource) and cls.__name__ not in (
                "BaseSource",
                "MultiTableSource",
            ):
                _logger.debug(
                    f"Found class {cls.__name__} in module {_module_info.name} which "
                    f"did not fully implement BaseSource. Skipping."
                )


# See top level `__init__.py` for an explanation
__pdoc__ = {}
for _obj in __all__:
    __pdoc__[_obj] = False
