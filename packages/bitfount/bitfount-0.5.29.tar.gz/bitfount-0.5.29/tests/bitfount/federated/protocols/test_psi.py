"""Tests for the private set intersection protocol."""
import re
from typing import Callable
from unittest.mock import Mock, create_autospec

import pytest
from pytest import fixture
from pytest_mock import MockerFixture

from bitfount.data.datasources.base_source import BaseSource
from bitfount.federated.algorithms.compute_intersection_rsa import (
    ComputeIntersectionRSA,
)
from bitfount.federated.exceptions import PSINoDataSourceError
from bitfount.federated.protocols import psi
from bitfount.federated.protocols.base import (
    _BaseModellerProtocol,
    _BaseProtocol,
    _BaseWorkerProtocol,
    registry,
)
from bitfount.federated.protocols.psi import (
    PrivateSetIntersection,
    _ModellerSide,
    _PSICompatibleAlgoFactory_,
    _PSICompatibleModeller,
    _PSICompatibleWorker,
    _WorkerSide,
)
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.schemas.utils import bf_dump, bf_load
from tests.utils.helper import create_datasource, unit_test


@unit_test
class TestWorkerSide:
    """Tests for the worker-side of the PrivateSetIntersection."""

    @fixture
    def mock_datasource(self) -> Mock:
        """Mock BaseSource."""
        mock_datasource: Mock = create_autospec(BaseSource, instance=True)
        return mock_datasource

    @fixture
    def mock_mailbox(self) -> Mock:
        """Mock WorkerMailbox."""
        mock_mailbox: Mock = create_autospec(_WorkerMailbox, instance=True)
        return mock_mailbox

    @fixture
    def worker_side_factory(self, mock_mailbox: Mock) -> Callable[[Mock], _WorkerSide]:
        """Factory to create WorkerSide instances from mock algorithms."""

        def _create(algo: Mock) -> _WorkerSide:
            return _WorkerSide(
                algorithm=algo,
                mailbox=mock_mailbox,
            )

        return _create

    async def test_run(
        self,
        mock_datasource: Mock,
        mock_mailbox: Mock,
        mocker: MockerFixture,
        worker_side_factory: Callable[[Mock], _WorkerSide],
    ) -> None:
        """Tests WorkerSide.run() for PrivateSetIntersection."""
        mock_algorithm: Mock = create_autospec(_PSICompatibleWorker, instance=True)
        mock_algorithm.public_key = Mock()
        worker_side: _WorkerSide = worker_side_factory(mock_algorithm)
        mock_modeller_psi_dataset = mocker.patch.object(
            worker_side, "_receive_modeller_psi_dataset"
        )

        await worker_side.run(mock_datasource)
        mock_modeller_psi_dataset.assert_awaited_once()

        mock_algorithm.initialise.assert_called_once_with(
            datasource=mock_datasource, columns_to_intersect=None, table=None
        )
        mock_algorithm.run.assert_called_once()
        mock_mailbox.get_task_complete_update.assert_called_once()

    async def test__receive_modeller_psi_dataset(
        self,
        mock_mailbox: Mock,
        mocker: MockerFixture,
        worker_side_factory: Callable[[Mock], _WorkerSide],
    ) -> None:
        """Tests that _receive_modeller_psi_dataset awaits _get_psi_dataset."""
        mock_algorithm: Mock = create_autospec(_PSICompatibleWorker, instance=True)
        mock_modeller_psi_dataset = mocker.patch(
            "bitfount.federated.protocols.psi._get_psi_dataset", return_value=["123"]
        )
        worker_side: _WorkerSide = worker_side_factory(mock_algorithm)
        data = await worker_side._receive_modeller_psi_dataset()
        mock_modeller_psi_dataset.assert_awaited_once_with(mock_mailbox)
        assert data[0] == 123

    async def test__send_public_key(
        self,
        mock_mailbox: Mock,
        mocker: MockerFixture,
        worker_side_factory: Callable[[Mock], _WorkerSide],
    ) -> None:
        """Tests that _send_public_key_to_modeller awaits _send_public_key."""
        mock_algorithm: Mock = create_autospec(_PSICompatibleWorker, instance=True)
        mock__send_public_key = mocker.patch(
            "bitfount.federated.protocols.psi._send_public_key"
        )
        worker_side: _WorkerSide = worker_side_factory(mock_algorithm)
        await worker_side._send_public_key_to_modeller(public_key=Mock)  # type: ignore[arg-type] # Reason: mocking for testing purposes # noqa: B950
        mock__send_public_key.assert_awaited_once()

    async def test__send_psi_data_to_modeller(
        self,
        mock_mailbox: Mock,
        mocker: MockerFixture,
        worker_side_factory: Callable[[Mock], _WorkerSide],
    ) -> None:
        """Tests that _send_psi_data_to_modeller awaits _send_psi_dataset_worker."""
        mock_algorithm: Mock = create_autospec(_PSICompatibleWorker, instance=True)
        mock__send_psi_data_to_modeller = mocker.patch(
            "bitfount.federated.protocols.psi._send_psi_dataset_worker"
        )
        worker_side: _WorkerSide = worker_side_factory(mock_algorithm)
        await worker_side._send_psi_data_to_modeller(dataset=([1, 2], [0, 2]))
        mock__send_psi_data_to_modeller.assert_awaited_once_with(
            (["1", "2"], ["0", "2"]), mock_mailbox
        )


@unit_test
class TestModellerSide:
    """Tests for the modeller-side of the PrivateSetIntersection."""

    @fixture
    def mock_datasource(self) -> Mock:
        """Mock BaseSource."""
        mock_datasource: Mock = create_autospec(BaseSource, instance=True)
        return mock_datasource

    @fixture
    def mock_mailbox(self) -> Mock:
        """Mock WorkerMailbox."""
        mock_mailbox: Mock = create_autospec(_ModellerMailbox, instance=True)
        return mock_mailbox

    @fixture
    def modeller_side_factory(
        self, mock_mailbox: Mock
    ) -> Callable[[Mock], _ModellerSide]:
        """Factory to create ModellerSide instances from mock algorithms."""

        def _create(algo: Mock) -> _ModellerSide:
            return _ModellerSide(
                algorithm=algo,
                datasource=Mock(),
                mailbox=mock_mailbox,
            )

        return _create

    async def test_run(
        self,
        mock_datasource: Mock,
        mock_mailbox: Mock,
        mocker: MockerFixture,
        modeller_side_factory: Callable[[Mock], _ModellerSide],
    ) -> None:
        """Tests ModellerSide.run() for PrivateSetIntersection."""
        mock_algorithm: Mock = create_autospec(_PSICompatibleModeller, instance=True)
        modeller_side: _ModellerSide = modeller_side_factory(mock_algorithm)
        mock__receive_public_key = mocker.patch.object(
            modeller_side, "_receive_public_key"
        )
        mock_get_psi_datasets_from_workers = mocker.patch(
            "bitfount.federated.protocols.psi._get_psi_datasets_from_workers"
        )
        await modeller_side.run()
        mock__receive_public_key.assert_awaited_once()
        mock_get_psi_datasets_from_workers.assert_awaited_once()
        mock_algorithm.initialise.assert_called_once()
        mock_algorithm.run.assert_called_once()

    async def test__send_psi_data_modeller(
        self,
        mock_datasource: Mock,
        mock_mailbox: Mock,
        mocker: MockerFixture,
        modeller_side_factory: Callable[[Mock], _ModellerSide],
    ) -> None:
        """Tests ModellerSide._send_psi_data_modeller() for PrivateSetIntersection."""
        mock_algorithm: Mock = create_autospec(_PSICompatibleModeller, instance=True)
        mock__send_psi_data_modeller = mocker.patch(
            "bitfount.federated.protocols.psi._send_psi_dataset_modeller"
        )
        modeller_side: _ModellerSide = modeller_side_factory(mock_algorithm)
        await modeller_side._send_psi_data_modeller(dataset=[1, 2])
        mock__send_psi_data_modeller.assert_awaited_once()

    async def test__receive_psi_datasets_from_workers(
        self,
        mock_datasource: Mock,
        mock_mailbox: Mock,
        mocker: MockerFixture,
        modeller_side_factory: Callable[[Mock], _ModellerSide],
    ) -> None:
        """Tests ModellerSide._receive_psi_datasets_from_workers() for PrivateSetIntersection."""  # noqa: B950
        mock_algorithm: Mock = create_autospec(_PSICompatibleModeller, instance=True)
        mock_get_psi_data = mocker.patch(
            "bitfount.federated.protocols.psi._get_psi_datasets_from_workers"
        )
        modeller_side: _ModellerSide = modeller_side_factory(mock_algorithm)
        await modeller_side._receive_psi_datasets_from_workers()
        mock_get_psi_data.assert_awaited_once()

    async def test__receive_public_key(
        self,
        mock_datasource: Mock,
        mock_mailbox: Mock,
        mocker: MockerFixture,
        modeller_side_factory: Callable[[Mock], _ModellerSide],
    ) -> None:
        """Tests ModellerSide._receive_public_key() for PrivateSetIntersection."""
        mock_algorithm: Mock = create_autospec(_PSICompatibleModeller, instance=True)
        mock__receive_public_key = mocker.patch(
            "bitfount.federated.protocols.psi._get_public_key", return_value=["pub_key"]
        )
        mock_load_public_key = mocker.patch(
            "bitfount.federated.protocols.psi.load_pem_public_key"
        )
        modeller_side: _ModellerSide = modeller_side_factory(mock_algorithm)
        await modeller_side._receive_public_key()
        mock__receive_public_key.assert_awaited_once_with(mock_mailbox)
        mock_load_public_key.assert_called_once()


@unit_test
class TestPrivateSetIntersection:
    """Test PrivateSetIntersection protocol."""

    @fixture(scope="function")
    def remote_algorithm(self) -> ComputeIntersectionRSA:
        """Returns remote algorithm."""
        return ComputeIntersectionRSA()

    def test_modeller(
        self, mock_modeller_mailbox: Mock, remote_algorithm: ComputeIntersectionRSA
    ) -> None:
        """Test modeller method."""
        datasource = create_datasource(classification=True)
        protocol_factory = PrivateSetIntersection(
            algorithm=remote_algorithm, datasource=datasource
        )
        protocol = protocol_factory.modeller(mailbox=mock_modeller_mailbox)
        for type_ in [
            _BaseProtocol,
            _BaseModellerProtocol,
            psi._ModellerSide,
        ]:
            assert isinstance(protocol, type_)

    def test_modeller_no_datasource_error(
        self, mock_modeller_mailbox: Mock, remote_algorithm: ComputeIntersectionRSA
    ) -> None:
        """Test modeller method raises error with no datasource."""
        protocol_factory = PrivateSetIntersection(algorithm=remote_algorithm)
        with pytest.raises(PSINoDataSourceError):
            protocol_factory.modeller(mailbox=mock_modeller_mailbox)

    def test_worker(
        self,
        mock_hub: Mock,
        mock_worker_mailbox: Mock,
        remote_algorithm: ComputeIntersectionRSA,
    ) -> None:
        """Test modeller method."""
        protocol_factory = PrivateSetIntersection(algorithm=remote_algorithm)
        protocol = protocol_factory.worker(mailbox=mock_worker_mailbox, hub=mock_hub)
        for type_ in [
            _BaseProtocol,
            _BaseWorkerProtocol,
            psi._WorkerSide,
        ]:
            assert isinstance(protocol, type_)

    def test__validate_algorithm_accepts(self) -> None:
        """Tests _validate_algorithm accepts compatible."""
        # Test with PSICompatibleAlgoFactory
        mock_algorithm: Mock = create_autospec(
            _PSICompatibleAlgoFactory_, instance=True
        )
        PrivateSetIntersection._validate_algorithm(mock_algorithm)

    def test__validate_algorithm_rejects(self) -> None:
        """Tests _validate_algorithm rejects incompatible."""
        mock_algorithm: Mock = Mock(spec_set=["__name__"])
        with pytest.raises(
            TypeError,
            match=re.escape(
                f"The {PrivateSetIntersection.__name__} protocol does not "
                f"support the {type(mock_algorithm).__name__} algorithm."
            ),
        ):
            PrivateSetIntersection._validate_algorithm(mock_algorithm)

    def test_run_protocol(self, mocker: MockerFixture) -> None:
        """Tests we can run a protocol."""
        algorithm = ComputeIntersectionRSA()
        # Mock out Modeller creation
        mock_modeller = mocker.patch(
            "bitfount.federated.protocols.base._Modeller", autospec=True
        )
        mock_modeller.return_value = mock_modeller  # for __init__
        mock_modeller.run.return_value = None

        protocol = PrivateSetIntersection(algorithm=algorithm)
        protocol.run(
            pod_identifiers=["fake/fake"],
            hub=Mock(),
            message_service=Mock(),
        )

        mock_modeller.run.assert_called_once_with(["fake/fake"], require_all_pods=False)


@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for PSI protocol."""

    def test_serialization(self) -> None:
        """Test Marshmallow Serialization for a ComputeIntersectionRSA algorithm."""
        algorithm_factory = ComputeIntersectionRSA()
        proto = PrivateSetIntersection(algorithm=algorithm_factory)
        dumped = bf_dump(proto)
        loaded = bf_load(dumped, registry)
        assert proto.class_name == loaded.class_name
        from tests.bitfount.backends.pytorch.models.test_models import assert_vars_equal

        assert_vars_equal(vars(proto.algorithm), vars(loaded.algorithm))

    def test_serialization_w_columns_table(self) -> None:
        """Test Marshmallow Serialization for a ComputeIntersectionRSA algorithm."""
        algorithm_factory = ComputeIntersectionRSA()
        proto = PrivateSetIntersection(
            algorithm=algorithm_factory,
            datasource=create_datasource(classification=True),
            datasource_columns=["test"],
            datasource_table="table",
            pod_columns=["test"],
            pod_table="table",
        )
        dumped = bf_dump(proto)
        loaded = bf_load(dumped, registry)
        assert proto.class_name == loaded.class_name
        assert loaded.pod_columns == proto.pod_columns
        assert loaded.pod_table == proto.pod_table
        # Check that the modeller's datasource and columns don't get serialized
        assert loaded._modeller_cols is None
        assert loaded._modeller_table is None
        assert loaded.datasource is None

    def test_dump(self) -> None:
        """Test protocol.dump()."""
        algorithm_factory = ComputeIntersectionRSA()
        proto = PrivateSetIntersection(algorithm=algorithm_factory)
        dumped = proto.dump()
        assert dumped["class_name"] == proto.class_name
        assert dumped["algorithm"]["class_name"] == algorithm_factory.class_name
