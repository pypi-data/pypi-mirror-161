"""Results Only protocol."""
from __future__ import annotations

import time
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    List,
    Optional,
    Protocol,
    Tuple,
    cast,
    runtime_checkable,
)

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from marshmallow import fields
import pandas as pd

from bitfount.data.datasources.base_source import BaseSource
import bitfount.federated.algorithms.base as algorithms
from bitfount.federated.exceptions import PSINoDataSourceError
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.pod_vitals import _PodVitals
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.protocols.base import (
    _BaseCompatibleAlgoFactory,
    _BaseModellerProtocol,
    _BaseProtocolFactory,
    _BaseWorkerProtocol,
)
from bitfount.federated.transport.modeller_transport import (
    _get_psi_datasets_from_workers,
    _get_public_key,
    _ModellerMailbox,
    _send_psi_dataset_modeller,
)
from bitfount.federated.transport.worker_transport import (
    _get_psi_dataset,
    _send_psi_dataset_worker,
    _send_public_key,
    _WorkerMailbox,
)
from bitfount.federated.types import SerializedProtocol
from bitfount.schemas.utils import bf_dump
from bitfount.types import T_FIELDS_DICT, T_NESTED_FIELDS

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub

logger = _get_federated_logger(__name__)


@runtime_checkable
class _PSICompatibleModeller(Protocol):
    """Defines modeller-side algorithm compatibility."""

    def initialise(
        self,
        datasource: BaseSource,
        public_key: RSAPublicKey,
        columns_to_intersect: Optional[List[str]] = None,
        table: Optional[str] = None,
        **kwargs: Any,
    ) -> List[int]:
        """Initialises the modeller-side algorithm."""
        ...

    def run(self, pod_set: List[int], modeller_set: List[int]) -> pd.DataFrame:
        """Runs the modeller-side algorithm."""
        ...


@runtime_checkable
class _PSICompatibleWorker(Protocol):
    public_key: RSAPublicKey

    def initialise(
        self,
        datasource: BaseSource,
        columns_to_intersect: Optional[List[str]] = None,
        table: Optional[str] = None,
        **kwargs: Any,
    ) -> List[int]:
        """Initialises the worker-side algorithm."""
        ...

    def run(self, modeller_set: List[int]) -> List[int]:
        """Runs the worker-side algorithm."""
        ...


class _ModellerSide(_BaseModellerProtocol):
    """Modeller side of the PrivateSetIntersection protocol."""

    algorithm: _PSICompatibleModeller
    datasource: BaseSource

    def __init__(
        self,
        *,
        algorithm: _PSICompatibleModeller,
        datasource: Optional[BaseSource] = None,
        columns_to_intersect: Optional[List[str]] = None,
        table: Optional[str] = None,
        mailbox: _ModellerMailbox,
        **kwargs: Any,
    ):
        if datasource is None:
            # Datasource is optional to match the parent class signature.
            raise PSINoDataSourceError(
                "You are trying to run a PSI task with no datasource. "
                "Please provide a datasource and try again."
            )
        self.datasource = datasource
        self.columns_to_intersect = columns_to_intersect
        self.table = table
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    async def _send_psi_data_modeller(self, dataset: List[int]) -> None:
        """Sends psi dataset to workers."""
        logger.debug("Sending PSI dataset to the worker.")
        # Change integers to strings so msgpack can handle them.
        str_dataset = [str(item) for item in dataset]
        await _send_psi_dataset_modeller(str_dataset, self.mailbox)

    async def _receive_public_key(self) -> RSAPublicKey:
        """Receives public key from worker."""
        logger.debug("Receiving PSI parameters")
        serialized_keys: List[bytes] = await _get_public_key(self.mailbox)
        # We only support psi with one pod, so get the first key only.
        serialized_key = serialized_keys[0]
        # Cast to RSAPublicKEy, as it is the expected key type.
        return cast(RSAPublicKey, load_pem_public_key(serialized_key))

    async def _receive_psi_datasets_from_workers(self) -> Tuple[List[int], List[int]]:
        """Receives psi datasets from worker."""
        logger.debug("Receiving PSI datasets")
        psi_datasets: List[
            Tuple[List[str], List[str]]
        ] = await _get_psi_datasets_from_workers(self.mailbox)
        # We only support psi with one pod, so get the first item of the list.
        psi_datasets_str = psi_datasets[0]
        # Change dataset to int.
        # The first list of the tuple is the pod set, and the second is the modeller set
        psi_datasets_int = (
            [int(item) for item in psi_datasets_str[0]],
            [int(item) for item in psi_datasets_str[1]],
        )
        return psi_datasets_int

    async def run(
        self,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Runs Modeller side of the protocol."""
        public_key = await self._receive_public_key()
        modeller_input = self.algorithm.initialise(
            public_key=public_key,
            datasource=self.datasource,
            columns_to_intersect=self.columns_to_intersect,
            table=self.table,
        )
        await self._send_psi_data_modeller(modeller_input)
        pod_set, modeller_set = await self._receive_psi_datasets_from_workers()
        modeller_results = self.algorithm.run(pod_set, modeller_set)
        await self.mailbox.send_task_complete_message()
        return modeller_results


class _WorkerSide(_BaseWorkerProtocol):
    """Worker side of the PrivateSetIntersection protocol."""

    algorithm: _PSICompatibleWorker

    def __init__(
        self,
        *,
        algorithm: _PSICompatibleWorker,
        columns_to_intersect: Optional[List[str]] = None,
        table: Optional[str] = None,
        mailbox: _WorkerMailbox,
        **kwargs: Any,
    ):
        self.columns_to_intersect = columns_to_intersect
        self.table = table
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    async def _receive_modeller_psi_dataset(self) -> List[int]:
        """Receives psi dataset from modeller."""
        logger.debug("Receiving PSI dataset from modeller.")
        str_dataset = await _get_psi_dataset(self.mailbox)
        return [int(item) for item in str_dataset]

    async def _send_public_key_to_modeller(self, public_key: RSAPublicKey) -> None:
        """Sends the public key for psi to modeller."""
        await _send_public_key(public_key, self.mailbox)

    async def _send_psi_data_to_modeller(
        self, dataset: Tuple[List[int], List[int]]
    ) -> None:
        """Sends the psi datasets back to the modeller."""
        # Change integers to strings so msgpack can handle them.
        str_tuple = (
            [str(item) for item in dataset[0]],
            [str(item) for item in dataset[1]],
        )
        await _send_psi_dataset_worker(str_tuple, self.mailbox)

    async def run(
        self,
        datasource: BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        pod_vitals: Optional[_PodVitals] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Runs Worker side of the protocol."""
        await self._send_public_key_to_modeller(self.algorithm.public_key)
        pod_set = self.algorithm.initialise(
            datasource=datasource,
            columns_to_intersect=self.columns_to_intersect,
            table=self.table,
        )
        modeller_set = await self._receive_modeller_psi_dataset()
        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()
        hashed_modeller_set = self.algorithm.run(modeller_set)
        await self._send_psi_data_to_modeller((pod_set, hashed_modeller_set))
        await self.mailbox.get_task_complete_update()


@runtime_checkable
class _PSICompatibleAlgoFactory_(_BaseCompatibleAlgoFactory, Protocol):
    """Defines algo factory compatibility."""

    def modeller(self, **kwargs: Any) -> _PSICompatibleModeller:
        """Creates a modeller-side algorithm."""
        ...

    def worker(self, **kwargs: Any) -> _PSICompatibleWorker:
        """Creates a worker-side algorithm."""
        ...


class PrivateSetIntersection(_BaseProtocolFactory):
    """Performs a private set intersection with the provided algorithm.

    For more details, look at the algorithm description to
    understand how the intersection is computed.

    Args:
        algorithm: The algorithm to run.
        datasource: The modeller's datasource.
        datasource_columns: The modeller's columns from their datasource
            on which the private set intersection will be computed as a
            list of strings. Defaults to None.
        datasource_table: The modeller's table from their datasource,
            if the datasource is multitable, on which the private set
            intersection will be computed as a string. Defaults to None.
        pod_columns: The pod's columns from their datasource
            on which the private set intersection will be computed as a
            list of strings. Defaults to None.
        pod_table: The pod's table from their datasource,
            if the datasource is multitable, on which the private set
            intersection will be computed as a string. Defaults to None.

    Attributes:
        name: The name of the protocol.
        algorithm: The algorithm to run. This must be compatible with the
            `PrivateSetIntersection` protocol.
        pod_columns: The pod's columns from their datasource
            on which the private set intersection will be computed as a
            list of strings. Defaults to None.
        pod_table: The pod's table from their datasource,
            if the datasource is multitable, on which the private set
            intersection will be computed as a string. Defaults to None.

    Raises:
        TypeError: If the `algorithm` is not compatible with the protocol.
        PSINoDataSourceError: If you are trying to run the protocol without
            a datasource.
    """

    algorithm: _PSICompatibleAlgoFactory_
    # We only need to serialize the pod columns & table
    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "pod_columns": fields.List(fields.String(default=None), allow_none=True),
        "pod_table": fields.String(allow_none=True),
    }
    nested_fields: ClassVar[T_NESTED_FIELDS] = {"algorithm": algorithms.registry}

    def __init__(
        self,
        *,
        algorithm: _PSICompatibleAlgoFactory_,
        datasource: Optional[BaseSource] = None,
        datasource_columns: Optional[List[str]] = None,
        datasource_table: Optional[str] = None,
        pod_columns: Optional[List[str]] = None,
        pod_table: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.datasource = datasource
        self._modeller_cols = datasource_columns
        self._modeller_table = datasource_table
        self.pod_columns = pod_columns
        self.pod_table = pod_table
        super().__init__(algorithm=algorithm, **kwargs)

    @classmethod
    def _validate_algorithm(
        cls,
        algorithm: _BaseCompatibleAlgoFactory,
    ) -> None:
        """Checks that `algorithm` is compatible with the protocol."""
        if not isinstance(
            algorithm,
            (_PSICompatibleAlgoFactory_,),
        ):
            raise TypeError(
                f"The {cls.__name__} protocol does not support "
                + f"the {type(algorithm).__name__} algorithm.",
            )

    def dump(self) -> SerializedProtocol:
        """Returns the JSON-serializable representation of the protocol."""
        return cast(SerializedProtocol, bf_dump(self))

    def modeller(self, mailbox: _ModellerMailbox, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the PrivateSetIntersection protocol."""
        algorithm = self.algorithm.modeller()
        return _ModellerSide(
            algorithm=algorithm,
            datasource=self.datasource,
            columns_to_intersect=self._modeller_cols,
            table=self._modeller_table,
            mailbox=mailbox,
            **kwargs,
        )

    def worker(
        self, mailbox: _WorkerMailbox, hub: BitfountHub, **kwargs: Any
    ) -> _WorkerSide:
        """Returns the worker side of the PrivateSetIntersection protocol."""
        return _WorkerSide(
            algorithm=self.algorithm.worker(hub=hub),
            columns_to_intersect=self.pod_columns,
            table=self.pod_table,
            mailbox=mailbox,
            **kwargs,
        )
