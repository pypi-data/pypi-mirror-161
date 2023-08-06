"""Tests classes and functions in bitfount/federated/aggregators/base.py."""

import datetime
from typing import cast

import numpy as np
import pandas as pd
import pytest
from pytest import fixture
import torch

from bitfount.federated.aggregators.base import AggregationType, _BaseAggregator
from bitfount.federated.exceptions import AggregatorError
from tests.utils.helper import unit_test


@fixture
def dataframe() -> pd.DataFrame:
    """Returns a dataframe."""
    return pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": ["7", "8", "9"]})


@unit_test
class TestBaseAggregator:
    """Tests _BaseAggregator methods."""

    @fixture
    def base_aggregator(self) -> _BaseAggregator:
        """Create _BaseAggregator for tests."""
        return _BaseAggregator()

    def test_get_type_with_mismatching_types(
        self, base_aggregator: _BaseAggregator, dataframe: pd.DataFrame
    ) -> None:
        """Test get_type with mismatching types raises AggregatorError."""
        with pytest.raises(AggregatorError):
            base_aggregator._get_type([dataframe, dataframe["a"].to_numpy()])

    @pytest.mark.parametrize("length", [1, 2, 5])
    def test_get_type_with_numpy_array(
        self, base_aggregator: _BaseAggregator, length: int
    ) -> None:
        """Test get_type with numpy array returns NUMPY_ARRAY."""
        assert (
            base_aggregator._get_type([np.array([1, 2, 3])] * length)
            == AggregationType.NUMPY_ARRAY
        )

    @pytest.mark.parametrize("length", [1, 2, 5])
    def test_get_type_with_pandas_dataframe(
        self, base_aggregator: _BaseAggregator, dataframe: pd.DataFrame, length: int
    ) -> None:
        """Test get_type with pandas dataframe returns PANDAS_DATAFRAME."""
        assert (
            base_aggregator._get_type([dataframe] * length)
            == AggregationType.PANDAS_DATAFRAME
        )

    @pytest.mark.parametrize("length", [1, 2, 5])
    def test_get_type_with_tensor_dictionary(
        self, base_aggregator: _BaseAggregator, length: int
    ) -> None:
        """Test get_type with tensor dictionary returns TENSOR."""
        assert (
            base_aggregator._get_type(
                [{"param1": cast(torch.Tensor, np.array([1, 2, 3]))}] * length
            )
            == AggregationType.TENSOR_DICT
        )

    def test_get_type_with_unsupported_type(
        self, base_aggregator: _BaseAggregator
    ) -> None:
        """Test get_type with unsupported type raises AggregatorError."""
        assert base_aggregator._get_type([object()]) == AggregationType.UNSUPPORTED

    def test_set_non_numeric_columns_with_mismatching_non_numeric_columns(
        self, base_aggregator: _BaseAggregator, dataframe: pd.DataFrame
    ) -> None:
        """Test set_non_numeric_columns with mismatching non_numeric columns."""
        dataframe2 = dataframe.copy(deep=True)
        dataframe2["c"] = ["8", "9", "10"]  # should be 7, 8, 9
        with pytest.raises(
            AggregatorError,
            match="Non-numeric columns must be the same. "
            "Column c has different values between workers.",
        ):
            base_aggregator._set_non_numeric_columns([dataframe, dataframe2])

    def test_set_non_numeric_columns_with_misordered_non_numeric_columns(
        self, base_aggregator: _BaseAggregator, dataframe: pd.DataFrame
    ) -> None:
        """Test set_non_numeric_columns with mis-ordered non_numeric columns.

        This tests that the order of the values in the non-numeric columns is important.
        """
        dataframe2 = dataframe.copy(deep=True)
        dataframe2["c"] = ["7", "9", "8"]  # should be 7, 8, 9
        with pytest.raises(
            AggregatorError,
            match="Non-numeric columns must be the same. "
            "Column c has different values between workers.",
        ):
            base_aggregator._set_non_numeric_columns([dataframe, dataframe2])

    def test_set_non_numeric_columns_sets_correct_columns(
        self, base_aggregator: _BaseAggregator, dataframe: pd.DataFrame
    ) -> None:
        """Test set_non_numeric_columns sets non-numeric columns correctly."""
        dataframe["d"] = [datetime.datetime.today()] * 3
        base_aggregator._set_non_numeric_columns([dataframe, dataframe])
        assert list(base_aggregator.non_numeric_columns) == ["c", "d"]
        np.testing.assert_array_equal(
            base_aggregator.non_numeric_columns["c"], dataframe["c"].to_numpy()
        )
        np.testing.assert_array_equal(
            base_aggregator.non_numeric_columns["d"],
            dataframe["d"].to_numpy(),
        )
