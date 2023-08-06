"""Testcases for all classes in bitfount/utils.py."""
import inspect
import logging
from pathlib import Path
import re
import sys
from typing import Generator, List, Literal, NoReturn, Tuple, Union, cast

from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
import numpy as np
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
from testbook import testbook

from bitfount.utils import (
    _add_this_to_list,
    _find_logger_filenames,
    _full_traceback,
    _get_mb_from_bytes,
    _get_object_source_code,
    _handle_fatal_error,
    _inspect_get_file,
    _is_notebook,
    _powinv,
    _powmod,
    one_hot_encode_list,
)
from tests.utils import PytestRequest
from tests.utils.helper import get_critical_logs, get_debug_logs, unit_test


@unit_test
class TestIsNotebook:
    """Tests is_notebook()."""

    def test_notebook(self) -> None:
        """Tests fit_all_datasets()."""
        return_val = _is_notebook()
        assert not return_val


@unit_test
class TestAddThisToList:
    """Tests add_this_to_list()."""

    def test_add_duplicate(self) -> None:
        """Tests adding duplicate."""
        this = 1
        lst = [1, 2, 3]
        lst = _add_this_to_list(this, lst)
        assert lst == [1, 2, 3]

    def test_add_none(self) -> None:
        """Tests adding none."""
        this = None
        lst = [1, 2, 3]
        lst = _add_this_to_list(this, lst)
        assert lst == [1, 2, 3]

    def test_add_new_value(self) -> None:
        """Tests adding new value."""
        this = 4
        lst = [1, 2, 3]
        lst = _add_this_to_list(this, lst)
        assert lst == [1, 2, 3, 4]

    def test_add_list(self) -> None:
        """Tests adding list."""
        this = [4]
        lst = [1, 2, 3]
        lst = _add_this_to_list(this, lst)
        assert lst == [1, 2, 3, 4]


@unit_test
class TestOneHotEncodeList:
    """Tests one_hot_encode_list."""

    @staticmethod
    def data(dims: int) -> Union[List[int], List[List[int]]]:
        """Fixture of input list (or 2D list) of integers."""
        if dims == 1:
            return [0, 1, 2, 1]
        elif dims == 2:
            return [[0, 1], [1, 2], [2, 1], [1, 0]]
        else:
            raise ValueError(f"Unsupported dimension: {dims}")

    @staticmethod
    def expected(dims: int) -> np.ndarray:
        """Fixture of expected OHE output array."""
        if dims == 1:
            return np.array(
                [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 1, 0]], dtype=np.uint8
            )
        elif dims == 2:
            return np.array(
                [
                    [1, 0, 0, 0, 1, 0],
                    [0, 1, 0, 0, 0, 1],
                    [0, 0, 1, 0, 1, 0],
                    [0, 1, 0, 1, 0, 0],
                ],
                dtype=np.uint8,
            )
        else:
            raise ValueError(f"Unsupported dimension: {dims}")

    @fixture(params=[1, 2], ids=["1D", "2D"])
    def data_and_expected(
        self, request: PytestRequest
    ) -> Tuple[Union[List[int], List[List[int]]], np.ndarray]:
        """Fixture combining data and expected for different dimensions."""
        return self.data(request.param), self.expected(request.param)

    def test_one_hot_encode_int_list(
        self, data_and_expected: Tuple[Union[List[int], List[List[int]]], np.ndarray]
    ) -> None:
        """Tests one_hot_encode_list for int list."""
        data, expected = data_and_expected
        ohe = one_hot_encode_list(data)
        assert np.array_equal(ohe, expected)

    def test_one_hot_encode_array_list(
        self, data_and_expected: Tuple[Union[List[int], List[List[int]]], np.ndarray]
    ) -> None:
        """Tests one_hot_encode_list for array list."""
        data, expected = data_and_expected
        data_arrays = [np.array(i) for i in data]
        assert isinstance(data_arrays, list)
        assert isinstance(data_arrays[0], np.ndarray)
        ohe = one_hot_encode_list(data_arrays)
        assert np.array_equal(ohe, expected)

    def test_one_hot_encode_array(
        self, data_and_expected: Tuple[Union[List[int], List[List[int]]], np.ndarray]
    ) -> None:
        """Tests one_hot_encode_list for array."""
        data, expected = data_and_expected
        data_array = np.asarray(data)
        assert isinstance(data_array, np.ndarray)
        ohe = one_hot_encode_list(data_array)
        assert np.array_equal(ohe, expected)

    def test_one_hot_encode_fails_3D(self) -> None:
        """Tests one hot encoding fails for 3D data."""
        data = [[[1], [2], [3]]]
        with pytest.raises(
            ValueError,
            match="Incorrect number of dimensions for one-hot encoding; "
            "expected 1 or 2, got 3",
        ):
            one_hot_encode_list(data)  # type: ignore[arg-type] # Reason: purpose of test # noqa: B950

    def test_one_hot_encode_fails_0D(self) -> None:
        """Tests one hot encoding fails for scalar data."""
        data = 1
        with pytest.raises(
            ValueError,
            match="Incorrect number of dimensions for one-hot encoding; "
            "expected 1 or 2, got 0",
        ):
            one_hot_encode_list(data)  # type: ignore[arg-type] # Reason: purpose of test # noqa: B950


@unit_test
def test_get_mb_from_bytes() -> None:
    """Tests get_mb_from_bytes works correctly."""
    # Test with whole number of MB bytes
    whole_mb = 2 * 1024 * 1024  # 2MB
    mb = _get_mb_from_bytes(whole_mb)
    assert mb.whole == 2
    assert mb.fractional == 2.0

    # Test with non-whole number of MB bytes
    non_whole_mb = whole_mb + 1
    mb = _get_mb_from_bytes(non_whole_mb)
    assert mb.whole == 2
    assert mb.fractional == non_whole_mb / (1024 * 1024)


@unit_test
class TestFatalErrorHandling:
    """Tests for fatal error handling functions."""

    def test__find_logger_filenames(self, tmp_path: Path) -> None:
        """Tests that _find_logger_filenames works correctly.

        Tests that it finds multiple filenames, but only those at the correct level.
        """
        # Set a base logger with INFO and a file handler for CRITICAL
        logger_1 = logging.getLogger("logger_1")
        logger_1.setLevel(logging.INFO)
        path_1 = tmp_path / "log_1.log"
        handler_1 = logging.FileHandler(path_1)
        handler_1.setLevel(logging.CRITICAL)
        logger_1.addHandler(handler_1)
        # Need to treat _this_ as the root logger as pytest messes with the root
        # logger handlers
        logger_1.parent = None

        # Set a child logger which will inherit the level from the base logger
        # and has a separate file handler at WARNING
        logger_2 = logging.getLogger("logger_1.logger_2")
        path_2 = tmp_path / "log_2.log"
        handler_2 = logging.FileHandler(path_2)
        handler_2.setLevel(logging.WARNING)
        logger_2.addHandler(handler_2)

        critical_log_files = _find_logger_filenames(
            logger_2, cast(Literal[50], logging.CRITICAL)
        )
        warning_log_files = _find_logger_filenames(
            logger_2, cast(Literal[30], logging.WARNING)
        )
        info_log_files = _find_logger_filenames(
            logger_2, cast(Literal[20], logging.INFO)
        )
        debug_filenames = _find_logger_filenames(
            logger_2, cast(Literal[10], logging.DEBUG)
        )

        # CRITICAL should contain both files, in reverse order
        assert critical_log_files == [str(path_2), str(path_1)]
        # WARNING should only contain the second file
        assert warning_log_files == [str(path_2)]
        # INFO should contain no files (i.e. be None) as no file handlers exist
        # for that level
        assert info_log_files is None
        # DEBUG should contain no files (i.e. be None) as the logger is not enabled
        # for that level
        assert debug_filenames is None

    @pytest.mark.parametrize(argnames="traceback_prelimited", argvalues=(True, False))
    def test__full_traceback_context_manager(
        self,
        monkeypatch: MonkeyPatch,
        traceback_prelimited: bool,
    ) -> None:
        """Tests that _full_traceback correctly manipulates sys.tracebacklimit."""
        limit = 10

        # Temporarily delete any previously set tracebacklimit
        monkeypatch.delattr("sys.tracebacklimit", raising=False)

        # Check condition before entering context manager
        if traceback_prelimited:
            sys.tracebacklimit = limit
            assert sys.tracebacklimit == limit
        else:
            assert not hasattr(sys, "tracebacklimit")

        with _full_traceback():
            # Should not have tracebacklimit set
            assert not hasattr(sys, "tracebacklimit")

        # Check post-condition after context manager
        if traceback_prelimited:
            assert sys.tracebacklimit == limit
        else:
            assert not hasattr(sys, "tracebacklimit")

    @pytest.fixture
    def temp_tb_limit(self) -> Generator[int, None, None]:
        """Temporarily manipulate tracebacklimit to ensure reset."""
        orig = sys.tracebacklimit
        temp_tb_limit = orig + 1
        sys.tracebacklimit = temp_tb_limit
        try:
            yield temp_tb_limit
        finally:
            sys.tracebacklimit = orig

    @pytest.mark.parametrize(
        argnames="cli_mode",
        argvalues=(True, False),
        ids=lambda x: f"cli_mode={x}",
    )
    @pytest.mark.parametrize(
        argnames="dev_mode",
        argvalues=(True, False),
        ids=lambda x: f"dev_mode={x}",
    )
    def test__handle_fatal_error(
        self,
        caplog: LogCaptureFixture,
        cli_mode: bool,
        dev_mode: bool,
        mocker: MockerFixture,
        monkeypatch: MonkeyPatch,
        temp_tb_limit: int,
    ) -> None:
        """Test _handle_fatal_error function under various configurations."""
        # Capture all logs
        caplog.set_level(logging.DEBUG)

        # Set config variables
        monkeypatch.setattr("bitfount.config.BITFOUNT_CLI_MODE", cli_mode)
        monkeypatch.setattr("bitfount.config.BITFOUNT_DEV_MODE", dev_mode)

        # Patch out log file finding
        mocker.patch(
            "bitfount.utils._find_logger_filenames",
            return_value=["/tmp/hello", "/tmp/world"],
        )

        # Create nested exception, with traceback, for us to use
        def _inner() -> NoReturn:
            raise Exception("This is the fatal error")

        def _outer() -> NoReturn:
            _inner()

        try:
            _outer()
        except Exception as exc:
            e = exc

        expected_exc_cls = SystemExit if cli_mode else Exception
        with pytest.raises(expected_exc_cls, match="^This is the fatal error$"):
            assert sys.tracebacklimit == temp_tb_limit
            _handle_fatal_error(e)

        # Check has reverted
        assert sys.tracebacklimit == temp_tb_limit

        if not dev_mode:
            # Summary in critical, full in debug
            critical_logs = get_critical_logs(caplog)
            assert (
                "This is the fatal error."
                " Full details logged to /tmp/hello, /tmp/world." == critical_logs
            )

            # Full stack trace in debug logs
            full_stack_logs = get_debug_logs(caplog, full_details=True)

            # Should be two log calls
            assert len(caplog.records) == 2
        else:
            # Full stack trace in critical logs
            full_stack_logs = get_critical_logs(caplog, full_details=True)

            # Should only be a single log call
            assert len(caplog.records) == 1

        # Full stack trace, so expect method names, keywords, line numbers, etc
        assert "This is the fatal error" in full_stack_logs
        assert "Full details logged to" not in full_stack_logs
        for func_name in ("test__handle_fatal_error", _outer.__name__, _inner.__name__):
            assert re.search(rf"line \d+, in {func_name}", full_stack_logs)
        assert 'raise Exception("This is the fatal error")' in full_stack_logs


@unit_test
class TestSourceCodeFunctionality:
    """Tests functions that are used to get the source code of an object."""

    def test__inspect_get_file_for_a_function(self, mocker: MockerFixture) -> None:
        """Tests that _inspect_get_file works correctly with a function."""
        mock_inspect_getfile = mocker.patch(
            "bitfount.utils.inspect.getfile", side_effect=inspect.getfile
        )

        def _test_func() -> None:
            """Test function."""
            pass

        file_path = _inspect_get_file(_test_func)
        assert file_path == _test_func.__code__.co_filename
        mock_inspect_getfile.assert_called_once_with(_test_func)

    def test__inspect_get_file_for_a_class(self) -> None:
        """Tests that _inspect_get_file works correctly with a class."""

        class TestClass:
            """Test class."""

            pass

        file_path = _inspect_get_file(TestClass)
        # Assert the file path is the path to this test file
        assert Path(file_path) == Path(__file__)
        assert file_path == sys.modules[TestClass.__module__].__file__

    def test__inspect_get_file_raises_a_type_error(self, mocker: MockerFixture) -> None:
        """Tests that _inspect_get_file raises a TypeError.

        This happens if the type of the object is not supported for returning the source
        code file path.
        """
        # Prevent the __module__ attribute of `TestClass` from being detected
        mocker.patch("bitfount.utils.hasattr", return_value=False)

        class TestClass:
            """Test class."""

            pass

        with pytest.raises(TypeError, match="Source for TestClass not found"):
            _inspect_get_file(TestClass)

    def test__get_object_source_code_in_a_notebook(self, mocker: MockerFixture) -> None:
        """Tests that _get_object_source_code works correctly in a notebook.

        The `_is_notebook` and `extract_symbols` functions are mocked out to simulate
        a notebook environment.
        """
        mock_is_notebook = mocker.patch(
            "bitfount.utils._is_notebook", return_value=True
        )
        mock_extract_symbols = mocker.patch(
            "bitfount.utils._get_ipython_extract_symbols",
            return_value=lambda x, y: (["test_source_code"], []),
        )

        class TestClass:
            """Test class."""

            pass

        source_code = _get_object_source_code(TestClass)
        assert source_code == "test_source_code"
        mock_is_notebook.assert_called_once()
        mock_extract_symbols.assert_called_once()

    def test_notebook_get_object_source_code(self, mocker: MockerFixture) -> None:
        """Tests that _get_object_source_code works correctly in a notebook.

        Testbook is used to execute `_get_object_source_code` inside the notebook.
        """
        with testbook(
            "tests/bitfount/resources/test_notebook.ipynb", execute=True
        ) as tb:
            # Get the source code of the dummy Blah class
            source = tb.cell_output_text(2)
            # Assert it is what is expected
            assert source == inspect.cleandoc(
                '''
                class Blah:
                    """This is just a dummy class."""

                    def blah(self) -> str:
                        """This is just a dummy method."""
                        return "dummy method return value"

                '''
            )


@unit_test
class TestGMP:
    """Tests the functions using gmpy2."""

    def test__powmod_no_gmpy(self, mocker: MockerFixture) -> None:
        """Tests that _powmod works without gmpy2."""
        mocker.patch("bitfount.utils.HAVE_GMP", False)
        py_pow = mocker.patch("bitfount.utils.pow")
        _powmod(2, 3, 11)
        py_pow.assert_called_once()

    def test__powmod_gmpy(self, mocker: MockerFixture) -> None:
        """Tests that _powmod works with gmpy2."""
        mocker.patch("bitfount.utils.HAVE_GMP", True)
        gmpy_pow = mocker.patch("bitfount.utils.gmpy2.powmod")
        _powmod(2, 3, 11)
        gmpy_pow.assert_called_once()

    def test__powinv_no_gmpy(self, mocker: MockerFixture) -> None:
        """Tests that _powinv works without gmpy2."""
        mocker.patch("bitfount.utils.HAVE_GMP", False)
        py_pow = mocker.patch("bitfount.utils.pow")
        _powinv(2, 11)
        py_pow.assert_called_once_with(2, -1, 11)

    def test__powinv_gmpy(self, mocker: MockerFixture) -> None:
        """Tests that _powinv works with gmpy2."""
        mocker.patch("bitfount.utils.HAVE_GMP", True)
        gmpy_pow = mocker.patch("bitfount.utils.gmpy2.invert")
        _powinv(2, 11)
        gmpy_pow.assert_called_once_with(2, 11)

    def test__powinv_gmpy_returns_zero(self, mocker: MockerFixture) -> None:
        """Tests that we default to pow if zero is returned."""
        mocker.patch("bitfount.utils.HAVE_GMP", True)
        mocker.patch("bitfount.utils.gmpy2.invert", return_value=0)
        py_pow = mocker.patch("bitfount.utils.pow")
        _powinv(2, 11)
        py_pow.assert_called_once_with(2, -1, 11)
