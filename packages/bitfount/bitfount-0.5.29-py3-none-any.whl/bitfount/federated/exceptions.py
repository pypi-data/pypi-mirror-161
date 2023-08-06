"""Custom exceptions for the federated package."""
from bitfount.exceptions import BitfountError


class BitfountTaskStartError(BitfountError, RuntimeError):
    """Raised when an issue occurs whilst trying to start a task with pods."""

    pass


class MessageHandlerNotFoundError(BitfountError, KeyError):
    """Error raised when registered message handler can't be found."""

    pass


class MessageRetrievalError(BitfountError, RuntimeError):
    """Raised when an error occurs whilst retrieving a message from message service."""

    pass


class PodConnectFailedError(BitfountError, TypeError):
    """The message service has not correctly connected the pod."""

    pass


class PodRegistrationError(BitfountError):
    """Error related to registering a Pod with BitfountHub."""

    pass


class PodResponseError(BitfountError):
    """Pod rejected or failed to respond to a task request."""

    pass


class PodNameError(BitfountError):
    """Error related to given Pod name."""

    pass


class PrivateSqlError(BitfountError):
    """An exception for any issues relating to the PrivateSQL algorithm."""

    pass


class SecureShareError(BitfountError):
    """Error related to SecureShare processes."""

    pass


class AggregatorError(BitfountError, ValueError):
    """Error related to Aggregator classes."""

    pass


class EncryptionError(BitfountError):
    """Error related to encryption processes."""

    pass


class EncryptError(EncryptionError):
    """Error when attempting to encrypt."""

    pass


class DecryptError(EncryptionError):
    """Error when attempting to decrypt."""

    pass


class DPParameterError(BitfountError):
    """Error if any of given dp params are not allowed."""

    pass


class PSIError(BitfountError):
    """Error related to the PrivateSetIntersection protocol."""

    pass


class BlindingError(PSIError):
    """Error when attempting to blind."""

    pass


class UnBlindingError(PSIError):
    """Error when attempting to unblind."""

    pass


class OutOfBoundsError(PSIError):
    """Error when a value is out of bounds."""

    pass


class PSINoDataSourceError(PSIError):
    """Error when modeller tries to run a PSI task without a datasource."""

    pass


class PSIMultiplePodsError(PSIError):
    """Error when modeller tries to run a PSI task on multiple pods."""

    pass


class PSIMultiTableError(PSIError):
    """Error when trying perform PSI on a multitable datasource without specifying a table name."""  # noqa: B950

    pass
