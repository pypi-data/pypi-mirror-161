"""Tests Aggregator."""
import re
from typing import Dict, List, Union, cast
from unittest.mock import Mock, create_autospec

import numpy as np
import pandas as pd
import pytest
from pytest import fixture

from bitfount.federated.aggregators.aggregator import (
    Aggregator,
    _ModellerSide,
    _WorkerSide,
)
from bitfount.federated.aggregators.base import AggregationType, _BaseAggregator
from bitfount.federated.exceptions import AggregatorError
from bitfount.federated.shim import BackendTensorShim
from bitfount.types import _SerializedWeights, _TensorLike
from tests.bitfount.federated.aggregators.util import assert_equal_weight_dicts
from tests.utils.helper import unit_test


@fixture
def dataframe() -> pd.DataFrame:
    """Returns a dataframe."""
    return pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": ["7", "8", "9"]})


@fixture
def tensor_shim() -> Mock:
    """Returns mock tensor_shim."""
    mock_tensor_shim: Mock = create_autospec(BackendTensorShim)
    mock_tensor_shim.to_list.side_effect = lambda x: x.tolist()
    mock_tensor_shim.to_tensor.side_effect = lambda x, dtype: np.asarray(x, dtype)
    return mock_tensor_shim


@unit_test
class TestModellerSide:
    """Test Aggregator ModellerSide."""

    @fixture
    def modeller_side(self, tensor_shim: Mock) -> _ModellerSide:
        """Create ModellerSide for tests."""
        return _ModellerSide(tensor_shim=tensor_shim)

    @fixture
    def weights(self) -> Dict[str, Union[int, float]]:
        """A mapping of pod identifiers to aggregation weights."""
        return {
            "user1/pod1": 1.0,
            "user2/pod2": 2,
        }

    @fixture
    def normalised_weights(self) -> Dict[str, float]:
        """The expected normalised weights of the weights fixture."""
        return {
            "user1/pod1": 1 / 3,
            "user2/pod2": 2 / 3,
        }

    @fixture
    def modeller_side_with_weights(
        self, tensor_shim: Mock, weights: Dict[str, Union[int, float]]
    ) -> _ModellerSide:
        """Modeller-side of vanilla aggregation with weighting."""
        return _ModellerSide(tensor_shim=tensor_shim, weights=weights)

    def test_weights_returns_none_if_none_supplied(
        self,
        modeller_side: _ModellerSide,
    ) -> None:
        """Test `weights` property returns None if no weights set."""
        # No weights supplied in this fixture so should be None
        assert modeller_side.weights is None

    def test_weights_returns_normalised_weights_if_supplied(
        self,
        modeller_side_with_weights: _ModellerSide,
        normalised_weights: Dict[str, float],
        weights: Dict[str, Union[int, float]],
    ) -> None:
        """Test `weights` property returns normalised weights if weights set.

        Also ensures that this returned mapping is NOT the underlying mapping instance.
        """
        assert modeller_side_with_weights.weights == normalised_weights
        # Check this is a _copy_ of the underlying weights
        assert modeller_side_with_weights.weights == modeller_side_with_weights._weights
        assert (
            modeller_side_with_weights.weights
            is not modeller_side_with_weights._weights
        )

    def test_run_with_tensor_dictionary(self, modeller_side: _ModellerSide) -> None:
        """Test run method."""
        parameter_updates: Dict[str, _SerializedWeights] = {
            "user1/pod1": {"hello": [1.0, 1.0, 1.0], "world": [2.0, 2.0, 2.0]},
            "user2/pod2": {"hello": [2.0, 2.0, 2.0], "world": [3.0, 3.0, 3.0]},
        }
        average = modeller_side.run(algorithm_outputs=parameter_updates)

        expected_result = {
            "hello": np.asarray([1.5, 1.5, 1.5]),
            "world": np.asarray([2.5, 2.5, 2.5]),
        }
        assert_equal_weight_dicts(average, expected_result)

    def test_run_with_weights_and_tensor_dictionary(
        self, modeller_side_with_weights: _ModellerSide
    ) -> None:
        """Test run method with unequal weighting."""
        parameter_updates: Dict[str, _SerializedWeights] = {
            "user1/pod1": {"hello": [1.5, 1.5, 1.5], "world": [3.0, 3.0, 3.0]},
            "user2/pod2": {"hello": [1.5, 1.5, 1.5], "world": [2.25, 2.25, 2.25]},
        }
        average = modeller_side_with_weights.run(algorithm_outputs=parameter_updates)

        expected_result = {
            "hello": np.asarray([1.5, 1.5, 1.5]),
            "world": np.asarray([2.5, 2.5, 2.5]),
        }
        assert_equal_weight_dicts(average, expected_result)

    def test_run_with_weights_throws_exception_extra_updates(
        self, modeller_side_with_weights: _ModellerSide
    ) -> None:
        """Test run throws an exception if unequal weights and extra pod.

        That is, the parameter updates contain an update from a pod that has
        no weighting.
        """
        parameter_updates: Dict[str, _SerializedWeights] = {
            "user1/pod1": {"hello": [1.5, 1.5, 1.5], "world": [3.0, 3.0, 3.0]},
            "user2/pod2": {"hello": [1.5, 1.5, 1.5], "world": [2.25, 2.25, 2.25]},
            "user3/pod3": {"hello": [1.5, 1.5, 1.5], "world": [2.25, 2.25, 2.25]},
        }

        with pytest.raises(
            AggregatorError,
            match=re.escape(
                "Aggregation weightings provided but found updates from unweighted "
                "pods in received parameter updates: user3/pod3"
            ),
        ):
            modeller_side_with_weights.run(algorithm_outputs=parameter_updates)

    def test_run_with_weights_throws_exception_missing_updates(
        self, modeller_side_with_weights: _ModellerSide
    ) -> None:
        """Test run throws an exception if unequal weights and missing pod.

        That is, the parameter updates are missing an expected pod which has a
        weighting associated with it.
        """
        parameter_updates: Dict[str, _SerializedWeights] = {
            "user2/pod2": {"hello": [1.5, 1.5, 1.5], "world": [2.25, 2.25, 2.25]},
        }

        with pytest.raises(
            AggregatorError,
            match=re.escape(
                "Aggregation weightings provided but missing updates from expected "
                "pods in received parameter updates: user1/pod1"
            ),
        ):
            modeller_side_with_weights.run(algorithm_outputs=parameter_updates)

    def test_run_throws_exception_different_params_in_updates(
        self, modeller_side_with_weights: _ModellerSide
    ) -> None:
        """Test run throws an exception if inconsistent updates are provided.

        In particular, that it throws an exception if the parameter names in each
        update are not the same.
        """
        parameter_updates: Dict[str, _SerializedWeights] = {
            "user1/pod1": {"hello": [1.5, 1.5, 1.5], "world": [3.0, 3.0, 3.0]},
            "user2/pod2": {"hello": [1.5, 1.5, 1.5], "not_world": [2.25, 2.25, 2.25]},
        }

        with pytest.raises(
            AggregatorError,
            match=re.escape(
                "Keys are not consistent between workers: "
                "all names should match ['hello', 'world']"
            ),
        ):
            modeller_side_with_weights.run(algorithm_outputs=parameter_updates)

    def test_run_with_pandas_dataframe(
        self, dataframe: pd.DataFrame, modeller_side: _ModellerSide
    ) -> None:
        """Test run method with pandas dataframe."""
        dataframe2 = dataframe.copy(deep=True)
        expected_df = dataframe.copy(deep=True)
        dataframe2["a"] = dataframe2["a"] * 2
        dataframe2["b"] = dataframe2["b"] * 2
        expected_df["a"] = expected_df["a"] * 1.5
        expected_df["b"] = expected_df["b"] * 1.5

        dataframes: Dict[str, pd.DataFrame] = {
            "user1/pod1": dataframe,
            "user2/pod2": dataframe2,
        }
        average = modeller_side.run(algorithm_outputs=dataframes)
        pd.testing.assert_frame_equal(
            average.sort_index(axis=1),
            expected_df.sort_index(axis=1),
        )

    def test_run_with_numpy_array(
        self, dataframe: pd.DataFrame, modeller_side: _ModellerSide
    ) -> None:
        """Test run method with pandas dataframe."""
        array2 = dataframe.copy(deep=True)["a"].to_numpy() * 2
        expected_array = dataframe.copy(deep=True)["a"].to_numpy() * 1.5

        dataframes: Dict[str, pd.DataFrame] = {
            "user1/pod1": dataframe["a"].to_numpy(),
            "user2/pod2": array2,
        }
        average = modeller_side.run(algorithm_outputs=dataframes)
        np.testing.assert_array_equal(average, expected_array)

    def test_validate_algorithm_outputs_unsupported_type(
        self,
        modeller_side: _ModellerSide,
    ) -> None:
        """Test validate_algorithm_outputs with an unsupported type raises an error."""
        with pytest.raises(
            AggregatorError,
            match="Algorithm outputs are not recognised. Currently only pandas "
            "dataframes, numpy arrays and tensor state dictionaries are supported.",
        ):
            modeller_side._validate_algorithm_outputs(
                [1, 2, 3], AggregationType.UNSUPPORTED
            )

    def test_validate_algorithm_outputs_tensor_mismatching_keys(
        self, modeller_side: _ModellerSide
    ) -> None:
        """Test validate_algorithm_outputs method with mismatching tensors."""
        parameter_updates: List[_SerializedWeights] = [
            {"hello": [1.0, 1.0, 1.0], "world": [2.0, 2.0, 2.0]},
            {"hello": [2.0, 2.0, 2.0], "not_world": [3.0, 3.0, 3.0]},
        ]
        with pytest.raises(
            AggregatorError,
            match=re.escape(
                "Keys are not consistent between workers: "
                "all names should match ['hello', 'world']"
            ),
        ):
            modeller_side._validate_algorithm_outputs(
                parameter_updates, AggregationType.TENSOR_DICT
            )

    def test_validate_algorithm_outputs_dataframe_mismatching_shapes(
        self, dataframe: pd.DataFrame, modeller_side: _ModellerSide
    ) -> None:
        """Test validate_algorithm_outputs method with mismatching tensors."""
        algorithm_outputs: List[pd.DataFrame] = [dataframe, dataframe[["a", "b"]]]
        with pytest.raises(
            AggregatorError,
            match=re.escape(
                "Algorithm outputs are not consistent between workers: "
                "all dataframes should have the same shape."
            ),
        ):
            modeller_side._validate_algorithm_outputs(
                algorithm_outputs, AggregationType.PANDAS_DATAFRAME
            )

    def test_validate_algorithm_outputs_dataframe_mismatching_columns(
        self, dataframe: pd.DataFrame, modeller_side: _ModellerSide
    ) -> None:
        """Test validate_algorithm_outputs method with mismatching tensors."""
        dataframe2 = dataframe.copy(deep=True)
        dataframe2.rename(columns={"c": "d"}, inplace=True)
        algorithm_outputs: List[pd.DataFrame] = [dataframe, dataframe2]
        with pytest.raises(
            AggregatorError,
            match=re.escape(
                "Algorithm outputs are not consistent between workers: "
                "all dataframes should have the same columns."
            ),
        ):
            modeller_side._validate_algorithm_outputs(
                algorithm_outputs, AggregationType.PANDAS_DATAFRAME
            )

    def test_validate_algorithm_outputs_numpy_array_mismatching_shapes(
        self, dataframe: pd.DataFrame, modeller_side: _ModellerSide
    ) -> None:
        """Test validate_algorithm_outputs method with mismatching tensors."""
        algorithm_outputs: List[np.ndarray] = [
            dataframe["a"].to_numpy(),
            dataframe[["a", "b"]].to_numpy(),
        ]
        with pytest.raises(
            AggregatorError,
            match=re.escape(
                "Algorithm outputs are not consistent between workers: "
                "all arrays should have the same shape."
            ),
        ):
            modeller_side._validate_algorithm_outputs(
                algorithm_outputs, AggregationType.NUMPY_ARRAY
            )

    def test_validate_algorithm_outputs_numpy_array_unsupported_dtype(
        self, dataframe: pd.DataFrame, modeller_side: _ModellerSide
    ) -> None:
        """Test validate_algorithm_outputs method with mismatching tensors."""
        algorithm_outputs: List[np.ndarray] = [
            dataframe["c"].to_numpy(),
            dataframe["c"].to_numpy(),
        ]
        with pytest.raises(
            AggregatorError,
            match=re.escape("Numpy array dtype object is not a number type."),
        ):
            modeller_side._validate_algorithm_outputs(
                algorithm_outputs, AggregationType.NUMPY_ARRAY
            )

    def test_validate_algorithm_outputs_numpy_array(
        self, dataframe: pd.DataFrame, modeller_side: _ModellerSide
    ) -> None:
        """Test numpy arrays pass validation."""
        algorithm_outputs: List[np.ndarray] = [
            dataframe["a"].to_numpy(),
            dataframe["a"].to_numpy(),
        ]
        modeller_side._validate_algorithm_outputs(
            algorithm_outputs, AggregationType.NUMPY_ARRAY
        )

    def test_validate_algorithm_outputs_pandas_dataframe(
        self, dataframe: pd.DataFrame, modeller_side: _ModellerSide
    ) -> None:
        """Test pandas dataframes pass validation."""
        algorithm_outputs: List[pd.DataFrame] = [dataframe, dataframe]
        modeller_side._validate_algorithm_outputs(
            algorithm_outputs, AggregationType.PANDAS_DATAFRAME
        )

    def test_validate_algorithm_outputs_tensor(
        self, dataframe: pd.DataFrame, modeller_side: _ModellerSide
    ) -> None:
        """Test tensor state dicts pass validation."""
        parameter_updates: List[_SerializedWeights] = [
            {"hello": [1.0, 1.0, 1.0], "world": [2.0, 2.0, 2.0]},
            {"hello": [2.0, 2.0, 2.0], "world": [3.0, 3.0, 3.0]},
        ]
        modeller_side._validate_algorithm_outputs(
            parameter_updates, AggregationType.TENSOR_DICT
        )


@unit_test
class TestWorkerSide:
    """Test Aggregator WorkerSide."""

    @fixture
    def worker_side(self) -> _WorkerSide:
        """Create WorkerSide for tests."""
        return _WorkerSide(tensor_shim=tensor_shim)  # type: ignore[arg-type] # Reason: tensor shim is mocked # noqa: B950

    async def test_run_with_tensor_dict(self, worker_side: _WorkerSide) -> None:
        """Test run method with tensor dictionary."""
        parameter_update = {"hello": [1, 1, 1], "world": [2, 2, 2]}
        output = await worker_side.run(
            {
                key: cast(_TensorLike, np.asarray(value))
                for key, value in parameter_update.items()
            }
        )
        assert output == parameter_update

    async def test_run_with_numpy_array(self, worker_side: _WorkerSide) -> None:
        """Test run method with numpy array."""
        algorithm_output = np.asarray([1, 1, 1])
        output = await worker_side.run(algorithm_output)
        np.testing.assert_array_equal(output, algorithm_output)

    async def test_run_with_pandas_dataframe(
        self, dataframe: pd.DataFrame, worker_side: _WorkerSide
    ) -> None:
        """Test run method with pandas dataframe."""
        output = await worker_side.run(dataframe)
        pd.testing.assert_frame_equal(output, dataframe)

    async def test_run_with_unrecognised_type(self, worker_side: _WorkerSide) -> None:
        """Test run method with unrecognised type."""
        with pytest.raises(
            AggregatorError,
            match="Unrecognised type received from algorithm.",
        ):
            await worker_side.run(object())  # type: ignore[call-overload] # Reason: Purpose of test # noqa: B950


@unit_test
class TestAggregator:
    """Test Aggregator."""

    def test_modeller(self, tensor_shim: Mock) -> None:
        """Test modeller method."""
        aggregator_factory = Aggregator()
        aggregator = aggregator_factory.modeller()
        for type_ in [_BaseAggregator, _ModellerSide]:
            assert isinstance(aggregator, type_)

    def test_worker(self, tensor_shim: Mock) -> None:
        """Test worker method."""
        aggregator_factory = Aggregator()
        aggregator = aggregator_factory.worker()
        for type_ in [_BaseAggregator, _WorkerSide]:
            assert isinstance(aggregator, type_)
