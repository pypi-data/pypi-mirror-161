"""General helpful utilities to be found here."""
from __future__ import annotations

from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
import importlib
import importlib.util
import inspect
import linecache
import logging
from pathlib import Path
import random
import sys
from types import ModuleType
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    Generator,
    Iterable,
    List,
    Literal,
    Mapping,
    NoReturn,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

import numpy as np
from sklearn.preprocessing import OneHotEncoder

__all__: List[str] = ["one_hot_encode_list", "seed_all"]

from bitfount import config

_logger = logging.getLogger(__name__)

DEFAULT_SEED: int = 42


def _is_notebook() -> bool:
    """Checks if code is being executed in a notebook or not."""
    try:
        # get_ipython() is always available in a notebook, no need to import
        shell = get_ipython().__class__.__name__  # type: ignore[name-defined] # Reason: captured by NameError # noqa: B950
        return bool(shell == "ZMQInteractiveShell")  # True if ran from Jupyter notebook
    except NameError:
        return False  # Standard Python interpreter


def _inspect_get_file(obj: Any) -> str:
    """This is a wrapper around `inspect.getfile` that works with IPython.

    This is required because `inspect.getfile` does not work with classes defined in a
    notebook due to them not having a `__file__` attribute. Functions in a notebook are
    unaffected.

    Raises:
        TypeError: If the object source code cannot be retrieved.
    """
    # Only classes need a workaround, if the object is not a class we can just fall back
    # to `inspect.getfile`.
    if not inspect.isclass(obj):
        return inspect.getfile(obj)

    # Lookup by parent module as in `inspect.getfile`. This is the flow for classes that
    # are not defined in a notebook.
    if hasattr(obj, "__module__"):
        object_ = sys.modules.get(obj.__module__)
        if object_ is not None and hasattr(object_, "__file__"):
            return str(object_.__file__)

    # If parent module is __main__, lookup by methods. This is the flow for classes that
    # are defined in a notebook.
    for _, member in inspect.getmembers(obj):
        if (
            inspect.isfunction(member)
            and obj.__qualname__ + "." + member.__name__ == member.__qualname__
        ):
            return inspect.getfile(member)

    # If all else fails, raise an error.
    raise TypeError(f"Source for {obj.__name__} not found.")


def _get_ipython_extract_symbols() -> Callable[[Any, Any], Tuple[List, List]]:
    """Returns the `extract_symbols` function from IPython.

    This should only be imported from an environment which has IPython installed.
    """
    from IPython.core.magics.code import (  # type: ignore[import] # Reason: No stubs for this # noqa: B950
        extract_symbols,
    )

    return extract_symbols  # type: ignore[no-any-return] # Reason: No stubs for this # noqa: B950


def _get_object_source_code(obj: Any) -> str:
    """Returns the source code for an object as a string.

    If the object is defined in a file, the function simply returns the result from
    `inspect.getsource`. If the object is defined in a notebook, a different approach
    must be taken to extract the source code.
    """
    if _is_notebook():
        extract_symbols = _get_ipython_extract_symbols()

        # Extract the source code from the cell the object is defined in as a string.
        cell_code = "".join(linecache.getlines(_inspect_get_file(obj)))
        # Extracts the first symbol (by name) that is defined in the cell that the
        # object is defined in. This should be the object itself.
        class_code: str = extract_symbols(cell_code, obj.__name__)[0][0]
        return class_code

    return inspect.getsource(obj)


def seed_all(seed_value: Optional[int] = None) -> None:
    """Sets random seed for `numpy`, `python.random` and any other relevant library.

    If `pytorch` is used as the backend, this is just a wrapper around the
    `seed_everything` function from `pytorch-lightning`.

    Args:
        seed_value: The seed value to use. If None, uses the default seed (42).

    :::info

    `PYTHONHASHSEED` is not set as an environment variable because this has no effect
    once the process has been started. If you wish to set this, you should set it
    yourself in your own environment before running python.

    :::
    """
    seed_value = DEFAULT_SEED if seed_value is None else seed_value

    # Try to seed other libraries that may be present
    # Torch
    try:
        import pytorch_lightning as pl

        _logger.debug(f"Setting seed of torch, random and numpy to {seed_value}")
        # This call takes care of setting the seed for all libraries including
        # random and numpy as well as pytorch. `workers=True` ensures that the workers
        # for the dataloaders are also seeded.
        pl.seed_everything(seed_value, workers=True)
    except ModuleNotFoundError:
        _logger.debug(f"Setting seed of random and numpy to {seed_value}")
        random.seed(seed_value)
        np.random.seed(seed_value)


def _add_this_to_list(
    this: Union[Any, Iterable[Any]], the_list: List[Any]
) -> List[Any]:
    """Adds this to list.

    Checks if `this` is an iterable, in which case it extends the provided list
    (unless it is a string). Otherwise it appends to the provided list if not None.

    Finally, it removes duplicates from the list and returns it.
    """
    if isinstance(this, Iterable) and not isinstance(this, str):
        the_list.extend(this)
    else:
        if this is not None:
            the_list.append(this)
    return list(set(the_list))


def _array_version(this: Union[Any, Iterable[Any]]) -> List[Any]:
    """Returns this as a list.

    Checks if 'this' is an iterable, in which case it returns it as a list (unless
    it's a string), otherwise it wraps it as a single element list.
    """
    if isinstance(this, Iterable) and not isinstance(this, str):
        return list(this)
    return [this]


def one_hot_encode_list(
    targets: Union[
        np.ndarray, Iterable[np.ndarray], Iterable[int], Iterable[Iterable[int]]
    ]
) -> np.ndarray:
    """Converts a list of targets into a list of one-hot targets."""
    arr_targets: np.ndarray = np.asarray(targets)

    # Can only encode 1D or 2D targets
    if not (1 <= arr_targets.ndim <= 2):
        raise ValueError(
            f"Incorrect number of dimensions for one-hot encoding; "
            f"expected 1 or 2, got {arr_targets.ndim}"
        )

    # OneHotEncoder needs a 2D numpy array so if this is 1D, needs reshape
    if arr_targets.ndim == 1:
        arr_targets = arr_targets.reshape(-1, 1)

    # Ensure output is ndarray of correct types
    encoder = OneHotEncoder(categories="auto", sparse=False, dtype=np.uint8)
    # sparse=False guarantees output of ndarray
    return cast(np.ndarray, encoder.fit_transform(arr_targets))


def _get_module_from_file(path_to_module: Path) -> ModuleType:
    """Imports a module from a file path and returns the module.

    Args:
        path_to_module: The path to the module file.

    Returns:
        The module.

    Raises:
        ImportError: If the module cannot be imported.
    """
    path = path_to_module.expanduser().absolute()
    module_name = path.stem

    # Load the module from the file without saving it to sys.modules
    # See: https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly  # noqa: B950
    spec = importlib.util.spec_from_file_location(module_name, path)
    try:
        # `spec` has type `ModuleSpec | None`. If it is None, an error is raised which
        # caught by the `try...except` block
        module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type] # Reason: See comment # noqa: B950
        spec.loader.exec_module(module)  # type: ignore[union-attr] # Reason: See comment # noqa: B950
    except Exception as ex:
        raise ImportError(f"Unable to load code from {path_to_module}") from ex

    return module


def _get_non_abstract_classes_from_module(path_to_module: Path) -> Dict[str, type]:
    """Returns non-abstract classes from a module path.

    Returns a dictionary of non-abstract class names and classes present within a
    module file which is given as a Path object.
    """
    module = _get_module_from_file(path_to_module)

    classes = {
        name: class_
        for name, class_ in vars(module).items()
        if inspect.isclass(class_) and not inspect.isabstract(class_)
    }

    return classes


# TypeVars for merge_list_of_dicts
KT = TypeVar("KT")  # Key type.
VT = TypeVar("VT")  # Value type.


def _merge_list_of_dicts(
    lod: Iterable[Mapping[KT, Union[VT, Iterable[VT]]]]
) -> Dict[KT, List[VT]]:
    """Converts a list of dicts into a dict of lists.

    Each element in the dicts should be a single element or a list of elements.
    Any list of elements will be flattened into the final list, any single
    elements will be appended.

    Args:
        lod: A list of dicts to merge.

    Returns:
        A dictionary of lists where each value is the merged values from the
        input list of dicts.
    """
    # Merge into singular lists rather than a list of dicts
    merged: DefaultDict[KT, List[VT]] = defaultdict(list)

    for i in lod:
        for k, v in i.items():
            # We ignore the mypy errors on the `extend` and `append` calls because
            # we don't know the type of v. Instead rely on the `try...except` block
            # for type safety
            try:
                # Attempt to extend first (for outputs and targets)
                merged[k].extend(v)  # type: ignore[arg-type]  # Reason: will TypeError if not Iterable[VT]  # noqa: B950
            except TypeError:
                # Otherwise if not iterable, append
                v = cast(VT, v)
                merged[k].append(v)

    return merged


@dataclass
class _MegaBytes:
    """Thin wrapper for bytes->MB conversion."""

    whole: int
    fractional: float


def _get_mb_from_bytes(num_bytes: int) -> _MegaBytes:
    """Converts a number of bytes into the number of megabytes.

    Returns a tuple of the number of whole megabytes and the number of megabytes
    as a float.
    """
    mb: float = num_bytes / (1024 * 1024)
    return _MegaBytes(int(mb), mb)


_LOG_LEVELS_STR = Literal[
    "CRITICAL",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
]
_LOG_LEVELS_NUM = Literal[
    50,  # logging.CRITICAL
    40,  # logging.ERROR
    30,  # logging.WARNING
    20,  # logging.INFO
    10,  # logging.DEBUG
]
_LOG_LEVELS = Union[_LOG_LEVELS_STR, _LOG_LEVELS_NUM]


def _find_logger_filenames(
    logger: logging.Logger, level: _LOG_LEVELS
) -> Optional[List[str]]:
    """Finds all files that are being logged to for a given logger and level."""
    # Convert to int-log-level if needed
    if isinstance(level, str):
        level = logging.getLevelName(level)
    level = cast(_LOG_LEVELS_NUM, level)

    # If logger is not enabled for target level, will never output
    if not logger.isEnabledFor(level):
        return None

    # Otherwise, iterate up through the logger hierarchy and note any FileHandler
    # files that will be output to for the target level.
    log_files: List[str] = []
    curr_logger: Optional[logging.Logger] = logger
    while curr_logger:
        handlers = curr_logger.handlers
        log_files.extend(
            h.baseFilename
            for h in handlers
            if isinstance(h, logging.FileHandler) and h.level <= level
        )
        curr_logger = curr_logger.parent  # will be None if root logger

    # Return either the list of file paths or None if no files
    # were found.
    if log_files:
        return log_files
    else:
        return None


_no_tb_limit_sentinel = object()

try:
    import gmpy2  # type: ignore[import] # Reason: see below

    # We only use 2 operations from gmpy2, and we force the output to be int
    HAVE_GMP = True
except ImportError:
    HAVE_GMP = False


def _powmod(base: int, power: int, mod: int) -> int:
    """Computes base^power modulo mod where base, power, mod are integers.

    Uses GMP if available.
    """
    if not HAVE_GMP:
        return pow(base, power, mod)
    else:
        return int(gmpy2.powmod(base, power, mod))


def _powinv(base: int, mod: int) -> int:
    """The multiplicative inverse of base in the integers modulo mod.

    Uses GMP if available.
    """
    if HAVE_GMP:
        try:
            inv = int(gmpy2.invert(base, mod))
            # According to documentation, gmpy2.invert might return 0 on
            # non-invertible element, although it seems to actually raise an
            # exception. To make sure that zero is not returned, we raise an exception
            if inv == 0:
                raise ZeroDivisionError("No inverse exists")
            return inv
        except ZeroDivisionError:
            return pow(base, -1, mod)
    else:
        return pow(base, -1, mod)


@contextmanager
def _full_traceback() -> Generator[None, None, None]:
    """Temporarily sets tracebacklimit to original limit."""
    # If sys.tracebacklimit has been set, we need to store its current value
    orig_limit: Union[int, object]
    try:
        orig_limit = sys.tracebacklimit
    except AttributeError:
        orig_limit = _no_tb_limit_sentinel

    # Reset traceback limit to default (done by deleting the attribute)
    if orig_limit is not _no_tb_limit_sentinel:
        del sys.tracebacklimit

    yield

    # Set back to original value again if needed
    if orig_limit is not _no_tb_limit_sentinel:
        sys.tracebacklimit = cast(int, orig_limit)


_fatal_logger = logging.getLogger("bitfount.fatal")


def _handle_fatal_error(
    ex: Exception,
    logger: logging.Logger = _fatal_logger,
    log_msg: Optional[str] = None,
) -> NoReturn:
    """Determines how to handle fatal errors depending on configuration.

    How the error is handled will depend on the configuration:
        - Normal, API-based use:
            - Exception is raised and system errors out.
            - Limited stack trace/error logged at CRITICAL.
            - Full stack trace logged at DEBUG.

        - Dev, API-based use:
            - Exception is raised and system errors out.
            - Full stack trace logged at CRITICAL.

        - Normal, CLI-based use:
            - Exception is captured and sys.exit() is called.
            - Limited stack trace/error logged at CRITICAL.
            - Full stack trace logged at DEBUG.

        - Dev, CLI-based use:
            - Exception is captured and sys.exit() is called.
            - Full stack trace logged at CRITICAL.

    Dev mode functionality can be configured by setting the BITFOUNT_DEV_MODE
    environment variable to True.
    CLI mode functionality can be configured by setting the BITFOUNT_CLI_MODE
    environment variable to True. This is automatically done if the Bitfount library
    is called from any of the CLI scripts provided.

    Args:
        ex: The exception to handle.
        logger: The logger to use for logging out details. If not provided a
            "bitfount.fatal" logger is used.
        log_msg: The log message to use. If not provided the str() representation
            of the exception is used.
    """
    # Create log_msg from exception if one not explicitly provided
    if not log_msg:
        log_msg = str(ex)

    # Determine how full stack trace will be logged
    if not config.BITFOUNT_DEV_MODE:
        # Will want to say "see debug log for more details"
        additional_log_msg = ""
        if debug_log_files := _find_logger_filenames(logger, "DEBUG"):
            if not log_msg.endswith("."):
                additional_log_msg += "."
            debug_log_files_str = ", ".join(debug_log_files)
            additional_log_msg += f" Full details logged to {debug_log_files_str}."
        logger.critical(log_msg + additional_log_msg)
        with _full_traceback():
            logger.debug(log_msg, exc_info=ex)
    else:
        with _full_traceback():
            logger.critical(log_msg, exc_info=ex)

    if config.BITFOUNT_CLI_MODE:
        # Exit instead of raising exception
        sys.exit(ex)
    else:
        # Exceptions get raised
        raise ex
