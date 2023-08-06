"""This package contains the core Bitfount codebase.

With the exception of `backends` which contains optional extra packages, every
subpackage or standalone module in this package must have an `__init__.py` file that
defines `__all__`.

Runners are explicitly excluded as they intended to be used by the scripts.
"""
#   ____  _ _    __                   _
#  | __ )(_) |_ / _| ___  _   _ _ __ | |_
#  |  _ \| | __| |_ / _ \| | | | '_ \| __|
#  | |_) | | |_|  _| (_) | |_| | | | | |_
#  |____/|_|\__|_|  \___/ \__,_|_| |_|\__|

import importlib as _importlib
import logging as _logging
import pkgutil as _pkgutil
import sys
from typing import Any
from typing import List as _List

from bitfount import (
    config,
    data,
    exceptions,
    federated,
    hub,
    metrics,
    models,
    storage,
    transformations,
    types,
    utils,
)
from bitfount.__version__ import __version__  # noqa: F401
from bitfount.config import *  # noqa: F403
from bitfount.data import *  # noqa: F403
from bitfount.exceptions import *  # noqa: F403
from bitfount.federated import *  # noqa: F403
from bitfount.hub import *  # noqa: F403
from bitfount.metrics import *  # noqa: F403
from bitfount.models import *  # noqa: F403
from bitfount.storage import *  # noqa: F403
from bitfount.transformations import *  # noqa: F403
from bitfount.types import *  # noqa: F403
from bitfount.utils import *  # noqa: F403

__all__: _List[str] = []

_logger = _logging.getLogger(__name__)

# Attempt to import backends if any exist
try:
    import bitfount.backends

    _backends_imported = True
except ModuleNotFoundError:
    _backends_imported = False

# If backends has been successfully imported, attempt to import each individual backend
# and add its __all__ to __all__
if _backends_imported:
    # Find all top-level subpackages in the backends package
    for _module_info in _pkgutil.iter_modules(
        bitfount.backends.__path__, f"{bitfount.backends.__name__}."
    ):
        _module = None
        # Attempt to import backend subpackage
        try:
            _module = _importlib.import_module(_module_info.name)
        except ImportError:
            pass

        # Add backend subpackage's __all__ to __all__
        if _module is not None:
            _imports: _List[str] = []
            try:
                _imports = _module.__dict__["__all__"]
                __all__.extend(_imports)
            except KeyError:
                _logger.error(f"Couldn't import {_module}: __all__ not defined.")

            # Add backend imports defined in __all__ to globals dictionary
            globals().update({k: getattr(_module, k) for k in _imports})


__all__.extend(config.__all__)
__all__.extend(data.__all__)
__all__.extend(exceptions.__all__)
__all__.extend(federated.__all__)
__all__.extend(hub.__all__)
__all__.extend(metrics.__all__)
__all__.extend(models.__all__)
__all__.extend(storage.__all__)
__all__.extend(transformations.__all__)
__all__.extend(types.__all__)
__all__.extend(utils.__all__)

# Currently, due to pdoc's reliance on `__all__`, we must iterate over `__all__`` to
# ignore every import in the documentation otherwise they become duplicated
# https://github.com/pdoc3/pdoc/issues/340
__pdoc__ = {}
for _obj in __all__:
    __pdoc__[_obj] = False

# Set stacktrace dependent on config
if not config.BITFOUNT_DEV_MODE:
    sys.tracebacklimit = config.BITFOUNT_TB_LIMIT

    # Jupyter/iPython has its own traceback system, so we need to handle that
    # differently
    try:
        # This function will be in scope if we're in jupyter/iPython
        ipython = get_ipython()  # type: ignore[name-defined] # Reason: see comment # noqa: B950, F405

        def _hide_traceback(
            exc_tuple: Any = None,
            filename: Any = None,
            tb_offset: Any = None,
            exception_only: Any = False,
            running_compiled_code: Any = False,
        ) -> Any:
            etype, value, tb = sys.exc_info()
            return ipython._showtraceback(
                etype, value, ipython.InteractiveTB.get_exception_only(etype, value)
            )

        ipython.showtraceback = _hide_traceback
    except NameError:
        # We are not in a Jupyter/iPython environment
        pass
