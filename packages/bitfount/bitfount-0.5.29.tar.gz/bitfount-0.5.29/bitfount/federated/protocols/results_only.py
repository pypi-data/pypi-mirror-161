"""Results Only protocol."""
from __future__ import annotations

import os
import time
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    List,
    Mapping,
    Optional,
    Protocol,
    Union,
    cast,
    overload,
    runtime_checkable,
)

from bitfount.data.datasources.base_source import BaseSource
from bitfount.federated.aggregators.base import (
    _AggregatorWorkerFactory,
    _BaseAggregatorFactory,
    _BaseModellerAggregator,
    _BaseWorkerAggregator,
)
from bitfount.federated.aggregators.base import registry as aggregators_registry
from bitfount.federated.aggregators.secure import _InterPodAggregatorWorkerFactory
from bitfount.federated.algorithms.base import registry as algorithms_registry
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModellerModelAlgorithm,
    _BaseWorkerModelAlgorithm,
)
from bitfount.federated.helper import _create_aggregator
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.model_reference import BitfountModelReference
from bitfount.federated.pod_vitals import _PodVitals
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.protocols.base import (
    _BaseCompatibleAlgoFactory,
    _BaseModellerProtocol,
    _BaseProtocolFactory,
    _BaseWorkerProtocol,
)
from bitfount.federated.transport.modeller_transport import (
    _ModellerMailbox,
    _send_model_parameters,
)
from bitfount.federated.transport.worker_transport import (
    _get_model_parameters,
    _InterPodWorkerMailbox,
    _WorkerMailbox,
)
from bitfount.federated.types import SerializedProtocol
from bitfount.schemas.utils import bf_dump
from bitfount.types import (
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    T_OPTIONAL_NESTED,
    DistributedModelProtocol,
    _SerializedWeights,
    _StrAnyDict,
    _Weights,
)

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub

logger = _get_federated_logger(__name__)


@runtime_checkable
class _ResultsOnlyCompatibleModellerAlgorithm(Protocol):
    """Defines modeller-side algorithm compatibility."""

    def initialise(
        self,
        **kwargs: Any,
    ) -> None:
        """Initialises the modeller-side algorithm."""
        ...

    def run(self, results: Mapping[str, Any]) -> _StrAnyDict:
        """Runs the modeller-side algorithm."""
        ...


@runtime_checkable
class _ResultsOnlyCompatibleWorkerAlgorithm(Protocol):
    """Defines worker-side algorithm compatibility."""

    @overload
    def initialise(
        self,
        datasource: BaseSource,
        **kwargs: Any,
    ) -> None:
        """Initialises the worker-side algorithm without DP."""
        ...

    @overload
    def initialise(
        self,
        datasource: BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the worker-side algorithm with DP."""
        ...

    def initialise(
        self,
        datasource: BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        model_params: Optional[_SerializedWeights] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the worker-side algorithm with DP and/or model parameters."""
        ...


@runtime_checkable
class _ResultsOnlyDataIncompatibleWorkerAlgorithm(
    _ResultsOnlyCompatibleWorkerAlgorithm, Protocol
):
    """Defines worker-side algorithm compatibility without datasource."""

    def run(self) -> Any:
        """Runs the worker-side algorithm."""
        ...


@runtime_checkable
class _ResultsOnlyDataCompatibleWorkerAlgorithm(
    _ResultsOnlyCompatibleWorkerAlgorithm, Protocol
):
    """Defines worker-side algorithm compatibility with datasource needed."""

    def run(self, data: BaseSource) -> Any:
        """Runs the worker-side algorithm."""
        ...


class _ModellerSide(_BaseModellerProtocol):
    """Modeller side of the ResultsOnly protocol."""

    algorithm: _ResultsOnlyCompatibleModellerAlgorithm
    aggregator: Optional[_BaseModellerAggregator]

    def __init__(
        self,
        *,
        algorithm: _ResultsOnlyCompatibleModellerAlgorithm,
        aggregator: Optional[_BaseModellerAggregator],
        mailbox: _ModellerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)
        self.aggregator = aggregator

    async def _send_parameters(self, new_parameters: _SerializedWeights) -> None:
        """Sends central model parameters to workers."""
        logger.debug("Sending global parameters to workers")
        await _send_model_parameters(new_parameters, self.mailbox)

    async def run(
        self,
        **kwargs: Any,
    ) -> Union[List[Any], Any]:
        """Runs Modeller side of the protocol."""
        self.algorithm.initialise()
        if isinstance(self.algorithm, _BaseModellerModelAlgorithm):
            initial_parameters: _Weights = self.algorithm.model.get_param_states()
            serialized_params = self.algorithm.model.serialize_params(
                initial_parameters
            )
            await self._send_parameters(serialized_params)
        eval_results = await self.mailbox.get_evaluation_results_from_workers()
        logger.info("Results recevied from Pods.")
        await self.mailbox.send_task_complete_message()

        modeller_results = self.algorithm.run(eval_results)

        if self.aggregator:
            return self.aggregator.run(modeller_results)

        return modeller_results


class _WorkerSide(_BaseWorkerProtocol):
    """Worker side of the ResultsOnly protocol."""

    algorithm: Union[
        _ResultsOnlyDataIncompatibleWorkerAlgorithm,
        _ResultsOnlyDataCompatibleWorkerAlgorithm,
    ]
    aggregator: Optional[_BaseWorkerAggregator]

    def __init__(
        self,
        *,
        algorithm: Union[
            _ResultsOnlyDataIncompatibleWorkerAlgorithm,
            _ResultsOnlyDataCompatibleWorkerAlgorithm,
        ],
        aggregator: Optional[_BaseWorkerAggregator],
        mailbox: _WorkerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)
        self.aggregator = aggregator

    async def _receive_parameters(self) -> _SerializedWeights:
        """Receives new global model parameters."""
        logger.debug("Receiving global parameters")
        return await _get_model_parameters(self.mailbox)

    async def run(
        self,
        datasource: BaseSource,
        pod_dp: Optional[DPPodConfig] = None,
        pod_vitals: Optional[_PodVitals] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Runs Worker side of the protocol."""
        if isinstance(self.algorithm, _BaseWorkerModelAlgorithm):
            # Receive the initial parameters here from the Modeller
            model_params = await self._receive_parameters()
        else:
            model_params = None

        # Pass model_params to initialise where we update the parameters
        self.algorithm.initialise(
            datasource=datasource,
            pod_dp=pod_dp,
            pod_identifier=pod_identifier,
            model_params=model_params,
        )

        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()
        try:
            self.algorithm = cast(
                _ResultsOnlyDataCompatibleWorkerAlgorithm, self.algorithm
            )
            results = self.algorithm.run(data=datasource)
        except TypeError:
            self.algorithm = cast(
                _ResultsOnlyDataIncompatibleWorkerAlgorithm, self.algorithm
            )
            results = self.algorithm.run()

        if self.aggregator:
            logger.debug("Aggregating results...")
            results = await self.aggregator.run(results)
            logger.debug("Aggregation complete.")

        await self.mailbox.send_evaluation_results(results)
        await self.mailbox.get_task_complete_update()


@runtime_checkable
class _ResultsOnlyCompatibleAlgoFactory(_BaseCompatibleAlgoFactory, Protocol):
    """Defines algo factory compatibility."""

    def modeller(self, **kwargs: Any) -> _ResultsOnlyCompatibleModellerAlgorithm:
        """Create a modeller-side algorithm."""
        ...


@runtime_checkable
class _ResultsOnlyCompatibleAlgoFactory_(_ResultsOnlyCompatibleAlgoFactory, Protocol):
    """Defines algo factory compatibility."""

    def worker(
        self, **kwargs: Any
    ) -> Union[
        _ResultsOnlyDataIncompatibleWorkerAlgorithm,
        _ResultsOnlyDataCompatibleWorkerAlgorithm,
    ]:
        """Create a worker-side algorithm."""
        ...


@runtime_checkable
class _ResultsOnlyCompatibleModelAlgoFactory(
    _ResultsOnlyCompatibleAlgoFactory, Protocol
):
    """Defines algo factory compatibility."""

    model: Union[DistributedModelProtocol, BitfountModelReference]
    pretrained_file: Optional[Union[str, os.PathLike]] = None

    def worker(
        self, hub: BitfountHub, **kwargs: Any
    ) -> Union[
        _ResultsOnlyDataIncompatibleWorkerAlgorithm,
        _ResultsOnlyDataCompatibleWorkerAlgorithm,
    ]:
        """Create a worker-side algorithm."""
        ...


class ResultsOnly(_BaseProtocolFactory):
    """Simply returns the results from the provided algorithm.

    This protocol is the most permissive protocol and only involves one round of
    communication. It simply runs the algorithm on the `Pod`(s) and returns the
    results as a list (one element for every pod) unless an aggregator is specified.

    Args:
        algorithm: The algorithm to run.
        aggregator: The aggregator to use for updating the algorithm results across all
            Pods participating in the task.  This argument takes priority over the
            `secure_aggregation` argument.
        secure_aggregation: Whether to use secure aggregation. This argument is
            overridden by the `aggregator` argument.

    Attributes:
        name: The name of the protocol.
        algorithm: The algorithm to run. This must be compatible with the `ResultsOnly`
            protocol.
        aggregator: The aggregator to use for updating the algorithm results.

    Raises:
        TypeError: If the `algorithm` is not compatible with the protocol.
    """

    # TODO: [BIT-1047] Consider separating this protocol into two separate protocols
    # for each algorithm. The algorithms may not be similar enough to benefit
    # from sharing one protocol.

    algorithm: Union[
        _ResultsOnlyCompatibleAlgoFactory_, _ResultsOnlyCompatibleModelAlgoFactory
    ]
    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {
        "algorithm": algorithms_registry,
        "aggregator": aggregators_registry,
    }
    optional_nested: ClassVar[T_OPTIONAL_NESTED] = ["aggregator"]

    def __init__(
        self,
        *,
        algorithm: Union[
            _ResultsOnlyCompatibleAlgoFactory_, _ResultsOnlyCompatibleModelAlgoFactory
        ],
        aggregator: Optional[_BaseAggregatorFactory] = None,
        secure_aggregation: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(algorithm=algorithm, **kwargs)
        self.aggregator: Optional[_BaseAggregatorFactory] = None

        if aggregator:
            self.aggregator = aggregator
        elif secure_aggregation:
            self.aggregator = _create_aggregator(secure_aggregation=secure_aggregation)
        else:
            logger.info("No aggregator specified. Will return a dictionary of results.")

    @classmethod
    def _validate_algorithm(
        cls,
        algorithm: _BaseCompatibleAlgoFactory,
    ) -> None:
        """Checks that `algorithm` is compatible with the protocol."""
        if not isinstance(
            algorithm,
            (
                _ResultsOnlyCompatibleAlgoFactory_,
                _ResultsOnlyCompatibleModelAlgoFactory,
            ),
        ):
            raise TypeError(
                f"The {cls.__name__} protocol does not support "
                + f"the {type(algorithm).__name__} algorithm.",
            )

    def dump(self) -> SerializedProtocol:
        """Returns the JSON-serializable representation of the protocol."""
        return cast(SerializedProtocol, bf_dump(self))

    def modeller(self, mailbox: _ModellerMailbox, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the ResultsOnly protocol."""
        if isinstance(self.algorithm, _ResultsOnlyCompatibleModelAlgoFactory):
            algorithm = self.algorithm.modeller(
                pretrained_file=self.algorithm.pretrained_file
            )
        else:
            algorithm = self.algorithm.modeller()
        return _ModellerSide(
            algorithm=algorithm,
            aggregator=self.aggregator.modeller() if self.aggregator else None,
            mailbox=mailbox,
            **kwargs,
        )

    def worker(
        self, mailbox: _WorkerMailbox, hub: BitfountHub, **kwargs: Any
    ) -> _WorkerSide:
        """Returns the worker side of the ResultsOnly protocol.

        Raises:
            TypeError: If the mailbox is not compatible with the aggregator.
        """
        worker_agg: Optional[_BaseWorkerAggregator] = None
        if self.aggregator is not None:
            if isinstance(self.aggregator, _AggregatorWorkerFactory):
                worker_agg = self.aggregator.worker()
            elif isinstance(self.aggregator, _InterPodAggregatorWorkerFactory):
                if not isinstance(mailbox, _InterPodWorkerMailbox):
                    raise TypeError(
                        "Inter-pod aggregators require an inter-pod worker mailbox."
                    )
                worker_agg = self.aggregator.worker(mailbox=mailbox)
            else:
                raise TypeError(
                    f"Unrecognised aggregator factory ({type(self.aggregator)}); "
                    f"unable to determine how to call .worker() factory method."
                )

        return _WorkerSide(
            algorithm=self.algorithm.worker(hub=hub),
            aggregator=worker_agg,
            mailbox=mailbox,
            **kwargs,
        )
