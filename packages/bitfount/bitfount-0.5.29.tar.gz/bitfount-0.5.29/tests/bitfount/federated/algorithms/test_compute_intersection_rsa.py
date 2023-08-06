"""Tests for the ComputeIntersectionRSA Algorithm."""
from pathlib import Path
import sys
from typing import TYPE_CHECKING, List, Tuple
from unittest.mock import Mock

from _pytest.fixtures import fixture
from _pytest.logging import LogCaptureFixture
from _pytest.tmpdir import TempPathFactory
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
import pandas as pd
import pytest
from pytest_mock import MockerFixture

from bitfount import BitfountHub, _Modeller
from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datasources.excel_source import ExcelSource
from bitfount.federated.algorithms.compute_intersection_rsa import (
    ComputeIntersectionRSA,
)
from bitfount.federated.algorithms.compute_intersection_rsa import (
    _ModellerSide as ModellerRSABlind,
)
from bitfount.federated.algorithms.compute_intersection_rsa import (
    _WorkerSide as WorkerRSABlind,
)
from bitfount.federated.algorithms.compute_intersection_rsa import _ModellerSide
from bitfount.federated.algorithms.compute_intersection_rsa import _WorkerSide
from bitfount.federated.encryption import _RSAEncryption
from bitfount.federated.exceptions import (
    BlindingError,
    OutOfBoundsError,
    PSIMultiplePodsError,
    PSIMultiTableError,
    UnBlindingError,
)
from bitfount.federated.utils import _ALGORITHMS, hash_set
from bitfount.schemas.utils import bf_dump, bf_load
from tests.utils.helper import (
    create_dataset,
    create_datasource,
    integration_test,
    unit_test,
)


class TestComputeIntersectionRSA:
    """Tests for the ComputeIntersectionRSA algorithm."""

    @fixture
    def rsa_key_pair(self) -> Tuple[RSAPrivateKey, RSAPublicKey]:
        """Fixture for RSA key pair."""
        return _RSAEncryption.generate_key_pair()

    @fixture
    def modeller_rsa_blind(self) -> ModellerRSABlind:
        """Fixture for the Modeller-side RSABLind()."""
        return ComputeIntersectionRSA().modeller()

    @fixture
    def worker_rsa_blind(self) -> WorkerRSABlind:
        """Fixture for the  Worker-side RSABLind()."""
        return ComputeIntersectionRSA().worker()

    @fixture
    def datasource(self) -> BaseSource:
        """Fixture for the DataFrameSource."""
        return create_datasource(classification=False)

    @fixture(scope="class")
    def multi_table_excel_file(self, tmp_path_factory: TempPathFactory) -> Path:
        """Path to multi table excel file."""
        dataframe = create_dataset(classification=False)[:10]
        tmp_path = tmp_path_factory.mktemp("temp_excel")
        filename = tmp_path / "test.xlsx"
        with pd.ExcelWriter(
            filename
        ) as writer:  # type: ignore[abstract] # Reason: This is the documented usage. # noqa: B950
            dataframe.to_excel(writer, index=False, sheet_name="Sheet1")
            dataframe.to_excel(writer, index=False, sheet_name="Sheet2")
        return filename

    @fixture(scope="class")
    def multi_table_excel_source(self, multi_table_excel_file: Path) -> ExcelSource:
        """Multi Table ExcelSource."""
        source = ExcelSource(multi_table_excel_file, sheet_name=["Sheet1", "Sheet2"])
        assert source.multi_table
        return source

    # Modeller-side tests
    @unit_test
    def test_random_factors(
        self, mocker: MockerFixture, modeller_rsa_blind: ModellerRSABlind
    ) -> None:
        """Tests that the random factors generation."""
        modeller_rsa_blind.n = 15
        modeller_rsa_blind.e = 3
        d = 3  # the corresponding private exponent (3*3 = 1 mod (3-1)*(5-1))
        random_numbers = [5, 2, 8, 7, 4, 2]
        mocker.patch(
            "bitfount.federated.algorithms.compute_intersection_rsa.secrets.randbelow",
            side_effect=random_numbers,
        )
        rand_factors = modeller_rsa_blind.generate_random_factors(n_elements=5)
        for (r_inv, r_enc), orig_r in zip(rand_factors, random_numbers[1:]):
            assert r_inv * orig_r % modeller_rsa_blind.n == 1
            assert r_enc**d % modeller_rsa_blind.n == orig_r

    @unit_test
    def test_blind_single_element(self, modeller_rsa_blind: ModellerRSABlind) -> None:
        """Tests that the blinding works as expected."""
        modeller_rsa_blind.n = 15
        modeller_rsa_blind.e = 3
        rf = (1, 7)
        x = 8
        assert modeller_rsa_blind.blind(x, rf) == 11

    @unit_test
    def test_blind_set(self, modeller_rsa_blind: ModellerRSABlind) -> None:
        """Tests that the binding a set works as expected."""
        modeller_rsa_blind.n = 15
        modeller_rsa_blind.e = 3
        modeller_rsa_blind.random_factors = [(1, 7), (6, 11)]
        modeller_rsa_blind.hashed_data = [8, 13]
        assert modeller_rsa_blind.blind_set() == [11, 8]

    @unit_test
    def test_blind_set_raises_error(self, modeller_rsa_blind: ModellerRSABlind) -> None:
        """Tests that the blinding a set raises error.

        An error should be raised if there are not enough random factors.
        """
        modeller_rsa_blind.n = 15
        modeller_rsa_blind.e = 3
        modeller_rsa_blind.random_factors = [(1, 7)]
        modeller_rsa_blind.hashed_data = [8, 13]
        with pytest.raises(BlindingError):
            modeller_rsa_blind.blind_set()

    @unit_test
    def test_unblind_single_element(self, modeller_rsa_blind: ModellerRSABlind) -> None:
        """Tests that the unblinding works as expected."""
        modeller_rsa_blind.n = 15
        modeller_rsa_blind.e = 3
        rf = (1, 7)
        x = 8
        assert modeller_rsa_blind.unblind(x, rf) == 8

    @unit_test
    def test_unblind_set(self, modeller_rsa_blind: ModellerRSABlind) -> None:
        """Tests that the unblinding a set works as expected."""
        modeller_rsa_blind.n = 15
        modeller_rsa_blind.e = 3
        modeller_rsa_blind.random_factors = [(1, 7), (6, 11)]
        modeller_rsa_blind.hashed_data = [8, 13]
        assert modeller_rsa_blind.unblind_set(modeller_rsa_blind.hashed_data) == [8, 3]

    @unit_test
    def test_unblind_set_raises_error(
        self, modeller_rsa_blind: ModellerRSABlind
    ) -> None:
        """Tests that the unblinding a set raises error.

        An error should be raised if there are not enough random factors.
        """
        modeller_rsa_blind.n = 15
        modeller_rsa_blind.e = 3
        modeller_rsa_blind.random_factors = [(1, 7)]
        modeller_rsa_blind.hashed_data = [8, 13]
        with pytest.raises(UnBlindingError):
            modeller_rsa_blind.unblind_set(modeller_rsa_blind.hashed_data)

    @unit_test
    def test_intersect(self, modeller_rsa_blind: ModellerRSABlind) -> None:
        """Tests that intersect returns expected results."""
        Y = pd.DataFrame(
            ["match1", "nomatch1", "match2", "nomatch2", "nomatch3", "match3"],
            columns=["column"],
        )
        B = ["hmatch1", "nomatch1", "hmatch2", "nomatch2", "nomatch3", "hmatch3"]
        bf = ["pod_v1", "pod_v2", "hmatch1", "pod_v3", "hmatch3", "pod_v4", "hmatch2"]
        expected_result = ["match1", "match2", "match3"]
        result = modeller_rsa_blind.intersect(
            Y, B, bf  # type:ignore[arg-type] # Reason: for testing purposes only.
        )
        assert result.values.tolist() == pd.DataFrame(expected_result).values.tolist()

    @integration_test
    def test_blinding_unblinding_works(
        self, modeller_rsa_blind: ModellerRSABlind
    ) -> None:
        """Tests that blinding and unblinding works as expected."""
        modeller_rsa_blind.hashed_data = [1, 2, 3, 4, 5, 6]
        modeller_rsa_blind.n = 15
        modeller_rsa_blind.e = 3
        modeller_rsa_blind.random_factors = modeller_rsa_blind.generate_random_factors(
            6
        )
        blinded_set = modeller_rsa_blind.blind_set()
        assert blinded_set == [
            x * r[1] % modeller_rsa_blind.n
            for x, r in zip(
                modeller_rsa_blind.hashed_data, modeller_rsa_blind.random_factors
            )
        ]
        unblinded_set = modeller_rsa_blind.unblind_set(blinded_set)
        assert unblinded_set == [
            x * r[0] % modeller_rsa_blind.n
            for x, r in zip(blinded_set, modeller_rsa_blind.random_factors)
        ]

    @pytest.mark.parametrize(
        "cols",
        [["TARGET"], ["TARGET", "A", "B", "C"]],
    )
    @unit_test
    def test_modeller_initialise_w_columns(
        self,
        cols: List[str],
        datasource: DataFrameSource,
        modeller_rsa_blind: ModellerRSABlind,
        rsa_key_pair: Tuple[RSAPrivateKey, RSAPublicKey],
    ) -> None:
        """Tests that the modeller is initialised correctly with columns."""
        # Limit the number of records for this unit test
        datasource.dataframe = datasource.dataframe[:10]
        data = datasource.get_data()
        modeller_rsa_blind.initialise(
            public_key=rsa_key_pair[1], datasource=datasource, columns_to_intersect=cols
        )
        assert modeller_rsa_blind.n == rsa_key_pair[1].public_numbers().n
        assert modeller_rsa_blind.e == rsa_key_pair[1].public_numbers().e
        assert modeller_rsa_blind.data.equals(data[cols])
        assert len(modeller_rsa_blind.hashed_data) == data.shape[0]
        assert len(modeller_rsa_blind.random_factors) == data.shape[0]

    @unit_test
    def test_modeller_initialise(
        self,
        datasource: DataFrameSource,
        modeller_rsa_blind: ModellerRSABlind,
        rsa_key_pair: Tuple[RSAPrivateKey, RSAPublicKey],
    ) -> None:
        """Tests that the modeller is initialised correctly."""
        # Limit the number of records for this unit test
        datasource.dataframe = datasource.dataframe[:10]
        data = datasource.get_data()
        modeller_rsa_blind.initialise(public_key=rsa_key_pair[1], datasource=datasource)
        assert modeller_rsa_blind.n == rsa_key_pair[1].public_numbers().n
        assert modeller_rsa_blind.e == rsa_key_pair[1].public_numbers().e
        assert modeller_rsa_blind.data.equals(data)
        assert len(modeller_rsa_blind.hashed_data) == data.shape[0]
        assert len(modeller_rsa_blind.random_factors) == data.shape[0]

    @pytest.mark.parametrize(
        "table,cols",
        [("Sheet1", ["TARGET"]), ("Sheet2", ["TARGET", "A", "B", "C"])],
    )
    @unit_test
    def test_modeller_initialise_multitable_cols(
        self,
        cols: List[str],
        modeller_rsa_blind: ModellerRSABlind,
        multi_table_excel_source: ExcelSource,
        rsa_key_pair: Tuple[RSAPrivateKey, RSAPublicKey],
        table: str,
    ) -> None:
        """Tests that the modeller is initialised for multi-table datasource."""  # noqa: B950
        # Set up modeller datasource
        modeller_datasource = multi_table_excel_source
        modeller_rsa_blind.initialise(
            public_key=rsa_key_pair[1],
            datasource=modeller_datasource,
            columns_to_intersect=cols,
            table=table,
        )
        assert modeller_rsa_blind.n == rsa_key_pair[1].public_numbers().n
        assert modeller_rsa_blind.e == rsa_key_pair[1].public_numbers().e
        assert modeller_rsa_blind.data is not None

    @pytest.mark.parametrize(
        "table",
        ["Sheet1", "Sheet2"],
    )
    @unit_test
    def test_modeller_initialise_multitable(
        self,
        modeller_rsa_blind: ModellerRSABlind,
        multi_table_excel_source: ExcelSource,
        rsa_key_pair: Tuple[RSAPrivateKey, RSAPublicKey],
        table: str,
    ) -> None:
        """Tests that the modeller is initialised for multi-table datasource."""  # noqa: B950
        # Set up modeller datasource
        modeller_datasource = multi_table_excel_source
        modeller_rsa_blind.initialise(
            public_key=rsa_key_pair[1],
            datasource=modeller_datasource,
            table=table,
        )
        assert modeller_rsa_blind.n == rsa_key_pair[1].public_numbers().n
        assert modeller_rsa_blind.e == rsa_key_pair[1].public_numbers().e
        assert modeller_rsa_blind.data is not None

    @unit_test
    def test_modeller_initialise_error_multitable(
        self,
        modeller_rsa_blind: ModellerRSABlind,
        multi_table_excel_source: ExcelSource,
        rsa_key_pair: Tuple[RSAPrivateKey, RSAPublicKey],
    ) -> None:
        """Tests that the modeller `initialise` raises error."""
        # Set up modeller datasource
        with pytest.raises(PSIMultiTableError):
            modeller_rsa_blind.initialise(
                public_key=rsa_key_pair[1],
                datasource=multi_table_excel_source,
            )

    @unit_test
    def test_modeller_hashing(self, modeller_rsa_blind: ModellerRSABlind) -> None:
        """Tests that the hashing function works."""
        dataset = [1, 2, 3, 4, 5, 6]
        hashed_set = hash_set(dataset, hashes.SHA256())
        expected_hash_set = []
        for item in dataset:
            digest = hashes.Hash(hashes.SHA256())
            digest.update(str(item).encode())
            data = digest.finalize()
            expected_hash_set.append(int.from_bytes(data, sys.byteorder))
        for hashed_value, expected_value in zip(hashed_set, expected_hash_set):
            # Check that the output of hashing is an integer.
            assert isinstance(hashed_value, int)
            assert hashed_value == expected_value

    @pytest.mark.parametrize(
        "dataset",
        [
            pd.DataFrame([1, 2, 3, 4, 5, 6], columns=["blah"]),
            pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=["name", "test"]),
        ],
    )
    @unit_test
    def test_hashing_df(self, dataset: pd.DataFrame) -> None:
        """Tests hashing for a dataframe object."""
        hashed_set = hash_set(dataset, hashes.SHA256())
        expected_hash_set = []
        for _, item in dataset.iterrows():
            item.name = None
            # Check that the 'name' column is not removed, just the index 'name' column
            if "name" in dataset.columns:
                assert dataset["name"] is not None
            digest = hashes.Hash(hashes.SHA256())
            digest.update(str(item).encode())
            data = digest.finalize()
            expected_hash_set.append(int.from_bytes(data, sys.byteorder))
        for hashed_value, expected_value in zip(hashed_set, expected_hash_set):
            # Check that the output of hashing is an integer.
            assert isinstance(hashed_value, int)
            assert hashed_value == expected_value

    @unit_test
    def test_modeller_run(
        self, mocker: MockerFixture, modeller_rsa_blind: ModellerRSABlind
    ) -> None:
        """Test modeller run method."""
        modeller_rsa_blind.data = ["item"]
        mock_unblind = mocker.patch.object(ModellerRSABlind, "unblind_set")
        mock_hash = mocker.patch(
            "bitfount.federated.algorithms.compute_intersection_rsa.hash_set"
        )
        mock_intersect = mocker.patch.object(ModellerRSABlind, "intersect")
        modeller_rsa_blind.run([1], [2])
        mock_unblind.assert_called_once_with([2])
        mock_hash.assert_called_once()
        mock_intersect.assert_called_once()

    # Worker-side tests
    @unit_test
    def test_worker_hasing(self, worker_rsa_blind: WorkerRSABlind) -> None:
        """Tests that the hashing function works."""
        dataset = [1, 2, 3, 4, 5, 6]
        hash_function = hashes.SHA512_256()
        hashed_set = hash_set(dataset, hash_function)
        expected_hash_set = []
        for item in dataset:
            digest = hashes.Hash(hash_function)
            digest.update(str(item).encode())
            data = digest.finalize()
            expected_hash_set.append(int.from_bytes(data, sys.byteorder))
        for hashed_value, expected_value in zip(hashed_set, expected_hash_set):
            # Check that the output of hashing is an integer.
            assert isinstance(hashed_value, int)
            assert hashed_value == expected_value

    @unit_test
    def test_worker_decrypt(self, worker_rsa_blind: WorkerRSABlind) -> None:
        """Tests that the decryption function works."""
        input_data = [1, 2, 3, 4, 5]
        worker_rsa_blind.data = input_data
        worker_rsa_blind.n = 15
        worker_rsa_blind.d = 3
        e = 3  # the corresponding private exponent (3*3 = 1 mod (3-1)*(5-1))
        data = worker_rsa_blind.decrypt_set(worker_rsa_blind.data)
        for item, expected_item in zip(data, input_data):
            assert item == pow(expected_item, worker_rsa_blind.d, worker_rsa_blind.n)
            assert pow(item, e, worker_rsa_blind.n) == expected_item

    @unit_test
    def test_worker_decrypt_raises_error(
        self, worker_rsa_blind: WorkerRSABlind
    ) -> None:
        """Tests that the decryption raises out of bounds error."""
        input_data = [1, 24, 3, 4, 5]
        worker_rsa_blind.data = input_data
        worker_rsa_blind.n = 15
        worker_rsa_blind.d = 3
        with pytest.raises(OutOfBoundsError):
            worker_rsa_blind.decrypt_set(worker_rsa_blind.data)

    @pytest.mark.parametrize(
        "cols",
        [["TARGET"], ["TARGET", "A", "B", "C"]],
    )
    @unit_test
    def test_worker_initialise_cols(
        self,
        cols: List[str],
        datasource: DataFrameSource,
        worker_rsa_blind: WorkerRSABlind,
    ) -> None:
        """Tests that the worker is initialised correctly."""
        # Limit the number of records for this unit test
        datasource.dataframe = datasource.dataframe[:10]
        data = datasource.get_data()
        decrypted_set = worker_rsa_blind.initialise(datasource, cols)
        assert worker_rsa_blind.data.equals(data[cols])
        assert len(decrypted_set) == data.shape[0]

    @unit_test
    def test_worker_initialise(
        self, datasource: DataFrameSource, worker_rsa_blind: WorkerRSABlind
    ) -> None:
        """Tests that the worker is initialised correctly."""
        # Limit the number of records for this unit test
        datasource.dataframe = datasource.dataframe[:10]
        data = datasource.get_data()
        decrypted_set = worker_rsa_blind.initialise(datasource)
        assert worker_rsa_blind.data.equals(data)
        assert len(decrypted_set) == data.shape[0]

    @pytest.mark.parametrize(
        "table,cols",
        [("Sheet1", ["TARGET"]), ("Sheet2", ["TARGET", "A", "B", "C"])],
    )
    @unit_test
    def test_worker_initialise_multitable_columns(
        self,
        cols: List[str],
        multi_table_excel_source: ExcelSource,
        table: str,
        worker_rsa_blind: WorkerRSABlind,
    ) -> None:
        """Tests that the worker is initialised correctly for a multitable."""
        worker_rsa_blind.initialise(
            multi_table_excel_source, columns_to_intersect=cols, table=table
        )
        assert worker_rsa_blind.data is not None

    @pytest.mark.parametrize(
        "table",
        ["Sheet1", "Sheet2"],
    )
    @unit_test
    def test_worker_initialise_multitable(
        self,
        multi_table_excel_source: ExcelSource,
        table: str,
        worker_rsa_blind: WorkerRSABlind,
    ) -> None:
        """Tests that the worker is initialised correctly for a multitable."""
        worker_rsa_blind.initialise(multi_table_excel_source, table=table)
        assert worker_rsa_blind.data is not None

    @unit_test
    def test_worker_initialise_error(
        self,
        caplog: LogCaptureFixture,
        multi_table_excel_source: ExcelSource,
        rsa_key_pair: Tuple[RSAPrivateKey, RSAPublicKey],
        worker_rsa_blind: WorkerRSABlind,
    ) -> None:
        """Tests that the worker `initialise` raises federated error."""
        err_string = "PrivateSetIntersection task on a multitable datasource"

        worker_rsa_blind.initialise(
            public_key=rsa_key_pair[1],
            datasource=multi_table_excel_source,
        )

        assert err_string in caplog.records[0].msg

    @unit_test
    def test_worker_run(
        self, mocker: MockerFixture, worker_rsa_blind: WorkerRSABlind
    ) -> None:
        """Tests the worker.run method."""
        mock_decrypt_set = mocker.patch.object(WorkerRSABlind, "decrypt_set")
        worker_rsa_blind.run([1, 2])
        mock_decrypt_set.assert_called_once_with([1, 2])

    # Integration tests
    @pytest.mark.parametrize(
        "cols",
        [["TARGET"], ["TARGET", "A", "B", "C"]],
    )
    @integration_test
    def test_e2e_rsa_blind_algorithm(
        self,
        cols: List[str],
        modeller_rsa_blind: ModellerRSABlind,
        worker_rsa_blind: WorkerRSABlind,
    ) -> None:
        """Tests RSABLind end-to-end."""
        dataset = create_dataset(classification=False)
        # Set up modeller datasource
        modeller_datasource = DataFrameSource(dataset[:10])
        # Set up worker datasource & columns
        worker_datasource = DataFrameSource(dataset[5:20])

        modeller_blinded_set = modeller_rsa_blind.initialise(
            public_key=worker_rsa_blind.public_key,
            datasource=modeller_datasource,
            columns_to_intersect=cols,
        )
        # Check correct attributes are set during initialisation for modeller
        assert modeller_rsa_blind.n == worker_rsa_blind.n
        assert modeller_rsa_blind.e == worker_rsa_blind.public_key.public_numbers().e
        assert modeller_rsa_blind.data.equals(dataset[:10][cols])
        assert modeller_rsa_blind.hashed_data == hash_set(
            dataset[:10][cols], modeller_rsa_blind.first_hash_function
        )
        assert len(modeller_rsa_blind.random_factors) == 10
        # Check initialisation output is as expected
        assert len(modeller_blinded_set) == 10
        assert [
            item * rf[1] % modeller_rsa_blind.n
            for item, rf in zip(
                modeller_rsa_blind.hashed_data, modeller_rsa_blind.random_factors
            )
        ] == modeller_blinded_set

        worker_decrypted_set = worker_rsa_blind.initialise(worker_datasource, cols)
        # Check correct attributes are set during initialisation for worker
        assert worker_rsa_blind.data.equals(dataset[5:20][cols])
        assert worker_decrypted_set == hash_set(
            worker_rsa_blind.decrypt_set(
                hash_set(worker_rsa_blind.data, worker_rsa_blind.first_hash_function)
            ),
            worker_rsa_blind.second_hash_function,
        )
        # Check worker and modeller run
        worker_decrypted_modeller_set = worker_rsa_blind.run(modeller_blinded_set)
        assert worker_decrypted_modeller_set == worker_rsa_blind.decrypt_set(
            modeller_blinded_set
        )
        # Check that the intersection is output correctly
        # We expect intersection at the last 5 rows in the modeller data
        intersection = modeller_rsa_blind.run(
            worker_decrypted_set, worker_decrypted_modeller_set
        )
        assert (
            intersection.values.tolist()
            == modeller_rsa_blind.data.iloc[5:10].values.tolist()
        )

    # Integration tests
    @pytest.mark.parametrize(
        "table,cols",
        [("Sheet1", ["TARGET"]), ("Sheet2", ["TARGET", "A", "B", "C"])],
    )
    @integration_test
    def test_e2e_rsa_blind_algorithm_multitable(
        self,
        cols: List[str],
        modeller_rsa_blind: ModellerRSABlind,
        multi_table_excel_source: ExcelSource,
        table: str,
        worker_rsa_blind: WorkerRSABlind,
    ) -> None:
        """Tests RSABLind end-to-end."""
        # Set up modeller datasource
        modeller_datasource = multi_table_excel_source
        # Set up worker datasource & columns
        worker_datasource = multi_table_excel_source

        modeller_blinded_set = modeller_rsa_blind.initialise(
            public_key=worker_rsa_blind.public_key,
            datasource=modeller_datasource,
            columns_to_intersect=cols,
            table=table,
        )
        # Check correct attributes are set during initialisation for modeller
        assert modeller_rsa_blind.n == worker_rsa_blind.n
        assert modeller_rsa_blind.e == worker_rsa_blind.public_key.public_numbers().e

        assert len(modeller_rsa_blind.random_factors) == 10
        # Check initialisation output is as expected
        assert len(modeller_blinded_set) == 10
        assert [
            item * rf[1] % modeller_rsa_blind.n
            for item, rf in zip(
                modeller_rsa_blind.hashed_data, modeller_rsa_blind.random_factors
            )
        ] == modeller_blinded_set

        worker_decrypted_set = worker_rsa_blind.initialise(
            worker_datasource, cols, table
        )
        # Check correct attributes are set during initialisation for worker
        assert worker_decrypted_set == hash_set(
            worker_rsa_blind.decrypt_set(
                hash_set(worker_rsa_blind.data, worker_rsa_blind.first_hash_function)
            ),
            worker_rsa_blind.second_hash_function,
        )
        # Check worker and modeller run
        worker_decrypted_modeller_set = worker_rsa_blind.run(modeller_blinded_set)
        assert worker_decrypted_modeller_set == worker_rsa_blind.decrypt_set(
            modeller_blinded_set
        )
        # Check that the intersection is output correctly
        # We expect intersection at the last 5 rows in the modeller data
        intersection = modeller_rsa_blind.run(
            worker_decrypted_set, worker_decrypted_modeller_set
        )

        assert intersection.values.tolist() == modeller_rsa_blind.data.values.tolist()

    @pytest.mark.parametrize(
        "cols",
        [["TARGET"], ["TARGET", "A", "B", "C"]],
    )
    @integration_test
    def test_step_by_step_rsa_blind_algorithm(
        self,
        cols: List[str],
        modeller_rsa_blind: ModellerRSABlind,
        worker_rsa_blind: WorkerRSABlind,
    ) -> None:
        """Test step-by-step ComputeIntersectionRSA Algorithm."""
        worker_rsa_blind = ComputeIntersectionRSA().worker()
        # worker is initialized with the hash functions to use,
        # and the public and private key parameters
        dataset = create_dataset(classification=False)

        # Set up modeller datasource
        modeller_datasource = DataFrameSource(dataset[:10])
        # Set up worker datasource
        worker_datasource = DataFrameSource(dataset[5:20])

        # Algorithm initialisation phases.
        # Modeller initialization:
        (
            modeller_rsa_blind.n,
            modeller_rsa_blind.e,
        ) = modeller_rsa_blind._get_public_key_numbers(worker_rsa_blind.public_key)

        # Load and hash the data with the first hash function for the modeller
        # Take only the 'TARGET' columns from the dataset
        modeller_rsa_blind.data = modeller_datasource.get_data()[cols]
        assert len(modeller_rsa_blind.data) == 10
        modeller_rsa_blind.hashed_data = hash_set(
            modeller_rsa_blind.data, modeller_rsa_blind.first_hash_function
        )
        assert len(modeller_rsa_blind.hashed_data) == 10

        # Check that enough random factors are generated on the modeller side
        modeller_rsa_blind.random_factors = modeller_rsa_blind.generate_random_factors(
            len(modeller_rsa_blind.data)
        )
        assert len(modeller_rsa_blind.random_factors) == 10

        # Check that blind_set works on the modeller side
        blinded_modeller_set = (
            modeller_rsa_blind.blind_set()
        )  # output of modeller_rsa_blind.initialise()
        assert len(blinded_modeller_set) == 10
        assert [
            item * rf[1] % modeller_rsa_blind.n
            for item, rf in zip(
                modeller_rsa_blind.hashed_data, modeller_rsa_blind.random_factors
            )
        ] == blinded_modeller_set

        # Worker Initialization
        # Load and hash the data with the first hash function for the worker
        # Take only the 'TARGET' columns from the dataset
        worker_rsa_blind.data = worker_datasource.get_data()[cols]
        assert len(worker_rsa_blind.data) == 15
        worker_hashed_data = hash_set(
            worker_rsa_blind.data, worker_rsa_blind.first_hash_function
        )
        assert len(worker_hashed_data) == 15

        # Decrypt and hash again the worker set
        decrypted_worker_set = worker_rsa_blind.decrypt_set(worker_hashed_data)
        assert len(decrypted_worker_set) == 15
        assert [
            pow(item, worker_rsa_blind.d, worker_rsa_blind.n)
            for item in worker_hashed_data
        ] == decrypted_worker_set

        # Hash again; this is the set that the modeller receives as the input for psi.
        hashed_decrypted_worker_set = hash_set(
            decrypted_worker_set, worker_rsa_blind.second_hash_function
        )
        assert len(hashed_decrypted_worker_set) == 15

        # Auxiliary checks for intermediary steps

        # Check that both worker and modeller have the same modulus
        assert worker_rsa_blind.n == modeller_rsa_blind.n
        # Check encryption and decryption return the same number
        enc = pow(2, modeller_rsa_blind.e, modeller_rsa_blind.n)
        dec = pow(enc, worker_rsa_blind.d, worker_rsa_blind.n)
        assert dec == 2

        # Check that the random factors can be cancelled out.
        for r_inv, r_enc in modeller_rsa_blind.random_factors:
            assert pow(r_enc, worker_rsa_blind.d, modeller_rsa_blind.n) == pow(
                r_inv, -1, modeller_rsa_blind.n
            )
            assert (
                pow(r_enc, worker_rsa_blind.d, modeller_rsa_blind.n)
                * r_inv
                % modeller_rsa_blind.n
                == 1
            )

        # Check that the hashes for the common elements match
        aux = modeller_rsa_blind.intersect(
            modeller_rsa_blind.data, modeller_rsa_blind.hashed_data, worker_hashed_data
        )
        # We expect intersection at the last 5 rows in the modeller data
        assert aux.values.tolist() == modeller_rsa_blind.data.iloc[5:10].values.tolist()

        # Running the algorithm phases.

        # Worker side:
        # Decrypt modeller blinded set.
        decrypted_modeller_set = worker_rsa_blind.decrypt_set(blinded_modeller_set)
        assert len(decrypted_modeller_set) == 10
        assert [
            pow(item, worker_rsa_blind.d, worker_rsa_blind.n)
            for item in blinded_modeller_set
        ] == decrypted_modeller_set

        # That's all on the worker side, moving on to the modeller_side.

        # First, unblind the modeller set received from the pod
        unblinded_set = modeller_rsa_blind.unblind_set(decrypted_modeller_set)
        assert len(unblinded_set) == 10
        assert [
            item * rf[0] % modeller_rsa_blind.n
            for item, rf in zip(
                decrypted_modeller_set, modeller_rsa_blind.random_factors
            )
        ] == unblinded_set

        # Hash the set with the second hash function
        hashed_unblinded_modeller_set = hash_set(
            unblinded_set, modeller_rsa_blind.second_hash_function
        )
        assert len(hashed_unblinded_modeller_set) == 10
        intersect = modeller_rsa_blind.intersect(
            modeller_rsa_blind.data,
            hashed_unblinded_modeller_set,
            hashed_decrypted_worker_set,
        )

        # Check that the intersection is output correctly
        # We expect intersection at the last 5 rows in the modeller data
        assert (
            intersect.values.tolist()
            == modeller_rsa_blind.data.iloc[5:10].values.tolist()
        )

    # MixIn.intersect() method tests
    @unit_test
    def test_compute_intersection_rsa_execute(
        self, datasource: BaseSource, mock_bitfount_session: Mock, mocker: MockerFixture
    ) -> None:
        """Test ComputeIntersectionRSA.execute()."""
        psi = ComputeIntersectionRSA()
        pod_identifiers = ["username/pod-id"]
        mock_modeller_run_method = mocker.patch.object(_Modeller, "run")
        mock__create_bitfounthub = mocker.patch(
            "bitfount.federated.mixins._create_bitfounthub"
        )
        mock___create_message_service = mocker.patch(
            "bitfount.federated.mixins._create_message_service"
        )
        mock_mock___get_idp_url = mocker.patch("bitfount.federated.mixins._get_idp_url")
        psi.execute(pod_identifiers=pod_identifiers, datasource=datasource)
        mock__create_bitfounthub.assert_called_once()
        mock___create_message_service.assert_called_once()
        mock_mock___get_idp_url.assert_called_once()
        mock_modeller_run_method.assert_called_once_with(
            pod_identifiers=pod_identifiers, require_all_pods=False
        )

    @unit_test
    def test_rsa_blind_execute_error(
        self,
        datasource: BaseSource,
        mock_bitfount_session: Mock,
    ) -> None:
        """Test ComputeIntersectionRSA.execute() raises error."""
        psi = ComputeIntersectionRSA()
        pod_identifiers = ["username/pod-id", "username/pod-id2"]
        with pytest.raises(PSIMultiplePodsError):
            psi.execute(
                pod_identifiers=pod_identifiers,
                datasource=datasource,
            )

    @unit_test
    def test_rsa_blind_execute_columns(
        self,
        datasource: DataFrameSource,
        mock_bitfount_session: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test ComputeIntersectionRSA.execute() with `columns` argument."""
        pod_identifiers = ["username/pod-id"]
        psi = ComputeIntersectionRSA(
            columns={"self": ["TARGET"], pod_identifiers[0]: ["TARGET"]}
        )
        mock_modeller_run_method = mocker.patch.object(_Modeller, "run")
        psi.execute(pod_identifiers=pod_identifiers, datasource=datasource)
        mock_modeller_run_method.assert_called_once_with(
            pod_identifiers=pod_identifiers, require_all_pods=False
        )


@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for rsa blind algorithm."""

    def test_serialization(self) -> None:
        """Test Marshmallow Serialization for private sql algorithm."""
        algorithm_factory = ComputeIntersectionRSA()
        dumped = bf_dump(algorithm_factory)
        loaded = bf_load(dumped, _ALGORITHMS)
        assert isinstance(loaded, ComputeIntersectionRSA)
        assert algorithm_factory.__dict__ == loaded.__dict__


# Static tests for algorithm-protocol compatibility
if TYPE_CHECKING:
    from typing import cast

    from bitfount.federated.protocols.psi import (
        _PSICompatibleAlgoFactory_,
        _PSICompatibleModeller,
        _PSICompatibleWorker,
    )

    # Check compatible with PrivateSetIntersection
    _algo_factory: _PSICompatibleAlgoFactory_ = ComputeIntersectionRSA()
    _modeller_side: _PSICompatibleModeller = _ModellerSide()
    _worker_side: _PSICompatibleWorker = _WorkerSide(
        hub=cast(BitfountHub, object()),
    )
