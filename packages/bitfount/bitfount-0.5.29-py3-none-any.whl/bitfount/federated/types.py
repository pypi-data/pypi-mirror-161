"""Useful types for Federated Learning."""
from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, List, Optional, Protocol, TypedDict, runtime_checkable

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from typing_extensions import NotRequired

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub


class SerializedModel(TypedDict):
    """Serialized representation of a model."""

    class_name: str
    hub: NotRequired[Optional[BitfountHub]]


class SerializedAlgorithm(TypedDict):
    """Serialized representation of an algorithm."""

    class_name: str  # value from AlgorithmType enum
    model: NotRequired[SerializedModel]


class SerializedAggregator(TypedDict):
    """Serialized representation of an aggregator."""

    class_name: str  # value from AggregatorType enum


class SerializedProtocol(TypedDict):
    """Serialized representation of a protocol."""

    class_name: str  # value from ProtocolType enum
    algorithm: SerializedAlgorithm
    aggregator: NotRequired[SerializedAggregator]


class ProtocolType(Enum):
    """Available protocol names from `bitfount.federated.protocol`."""

    FederatedAveraging = "bitfount.FederatedAveraging"
    ResultsOnly = "bitfount.ResultsOnly"
    PrivateSetIntersection = "bitfount.PrivateSetIntersection"


class AlgorithmType(Enum):
    """Available algorithm names from `bitfount.federated.algorithm`."""

    FederatedModelTraining = "bitfount.FederatedModelTraining"
    ModelTrainingAndEvaluation = "bitfount.ModelTrainingAndEvaluation"
    ModelEvaluation = "bitfount.ModelEvaluation"
    ColumnAverage = "bitfount.ColumnAverage"
    SqlQuery = "bitfount.SqlQuery"
    PrivateSqlQuery = "bitfount.PrivateSqlQuery"
    ComputeIntersectionRSA = "bitfount.ComputeIntersectionRSA"


class AggregatorType(Enum):
    """Available aggregator names from `bitfount.federated.aggregator`."""

    Aggregator = "bitfount.Aggregator"
    SecureAggregator = "bitfount.SecureAggregator"


class _PodResponseType(Enum):
    """Pod response types sent to `Modeller` on a training job request."""

    # Common response types
    ACCEPT = auto()

    # /api/access response types
    NO_ACCESS = auto()
    INVALID_PROOF_OF_IDENTITY = auto()
    UNAUTHORISED = auto()
    NO_PROOF_OF_IDENTITY = auto()


class _DataLessAlgorithm:
    """Base algorithm class for tagging purposes.

    Used in algorithms for which data loading is done at runtime.
    """

    ...


_RESPONSE_MESSAGES = {
    # Common response messages
    _PodResponseType.ACCEPT: "Job accepted",
    # /api/access response messages
    _PodResponseType.NO_ACCESS: "There are no permissions for this modeller/pod combination.",  # noqa: B950
    _PodResponseType.INVALID_PROOF_OF_IDENTITY: "Unable to verify identity; ensure correct login used.",  # noqa: B950
    _PodResponseType.UNAUTHORISED: "Insufficient permissions for the requested task on this pod.",  # noqa: B950
    _PodResponseType.NO_PROOF_OF_IDENTITY: "Unable to verify identity, please try again.",  # noqa: B950
}


@runtime_checkable
class _TaskRequestMessageGenerator(Protocol):
    """Callback protocol describing a task request message generator."""

    def __call__(
        self,
        serialized_protocol: SerializedProtocol,
        pod_identifiers: List[str],
        aes_key: bytes,
        pod_public_key: RSAPublicKey,
    ) -> bytes:
        """Function signature for the callback."""
        ...
