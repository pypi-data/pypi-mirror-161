"""Helper module for federated transport."""
import asyncio
from functools import wraps
import logging
from statistics import mean
from typing import (
    Any,
    Awaitable,
    Callable,
    Collection,
    Dict,
    Final,
    Mapping,
    Optional,
    Sequence,
    TypeVar,
    Union,
    cast,
    overload,
)

from grpc import RpcError, StatusCode

from bitfount.federated.transport.exceptions import BitfountMessageServiceError

_logger = logging.getLogger(__name__)


def _average_training_metrics(
    validation_metrics: Sequence[Mapping[str, str]]
) -> Dict[str, float]:
    """Average training metrics from each worker."""
    averaged_metrics = dict()
    if validation_metrics:
        # What should happen if one (or all) of the pods does not respond in time?
        for metric_key in validation_metrics[0]:
            averaged_metrics[metric_key] = mean(
                float(worker_metrics[metric_key])
                for worker_metrics in validation_metrics
            )
    return averaged_metrics


_RETRY_STATUS_CODES: Final = {
    sc
    for sc in StatusCode
    if sc
    not in (
        # because this means it worked
        StatusCode.OK,
        # because this means it doesn't need to be done again
        StatusCode.ALREADY_EXISTS,
        # because this means it will never work
        StatusCode.UNIMPLEMENTED,
    )
}
_DEFAULT_TIMEOUT: Final = 20.0
_DEFAULT_MAX_RETRIES: Final = 3
_DEFAULT_BACKOFF_FACTOR: Final = 1

# These should be replaced with ParamSpec versions once
# https://github.com/python/mypy/issues/11855 is resolved
_F = TypeVar("_F", bound=Callable[..., Awaitable[Any]])


@overload
def _auto_retry_grpc(
    original_rpc_func: _F,
    *,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    backoff_factor: int = _DEFAULT_BACKOFF_FACTOR,
    additional_no_retry_status_codes: Optional[Collection[StatusCode]] = None,
) -> _F:
    """Applies automatic retries to gRPC calls when encountering specific errors."""
    ...


@overload
def _auto_retry_grpc(
    original_rpc_func: None = None,
    *,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    backoff_factor: int = _DEFAULT_BACKOFF_FACTOR,
    additional_no_retry_status_codes: Optional[Collection[StatusCode]] = None,
) -> Callable[[_F], _F]:
    """Applies automatic retries to gRPC calls when encountering specific errors."""
    ...


def _auto_retry_grpc(
    original_rpc_func: Optional[_F] = None,
    *,
    max_retries: int = _DEFAULT_MAX_RETRIES,
    backoff_factor: int = _DEFAULT_BACKOFF_FACTOR,
    additional_no_retry_status_codes: Optional[Collection[StatusCode]] = None,
) -> Union[_F, Callable[[_F], _F]]:
    """Applies automatic retries to gRPC calls when encountering specific errors.

    Wraps the target gRPC call in a retry mechanism which will reattempt
    the call if a retryable gRPC error response is received.

    Utilises an exponential backoff to avoid flooding the request and to give
    time for the issue to resolve itself.

    Can be used as either an argumentless decorator (@_auto_retry_grpc) or a
    decorator with args (@_auto_retry_grpc(...)).
    """
    if additional_no_retry_status_codes:
        _additional_no_retry_status_codes = set(additional_no_retry_status_codes)
    else:
        _additional_no_retry_status_codes = set()

    def _decorate(grpc_func: _F) -> _F:
        """Apply decoration to target request function."""

        @wraps(grpc_func)
        async def _wrapped_async_grpc_func(*args: Any, **kwargs: Any) -> Any:
            """Wraps target gRPC function in retry capability.

            Adds automatic retry, backoff, and logging.
            """
            # Set default timeout if one not provided
            timeout = kwargs.get("timeout", None)
            if timeout is None:
                logging.debug(
                    f"No gRPC timeout provided,"
                    f" setting to default timeout ({_DEFAULT_TIMEOUT}s)"
                )
                kwargs["timeout"] = _DEFAULT_TIMEOUT

            retry_count = 0

            while retry_count <= max_retries:
                final_retry = retry_count == max_retries

                # Attempt to make wrapped call and handle if it doesn't work
                # as expected
                try:
                    return await grpc_func(*args, **kwargs)
                except RpcError as ex:
                    # If an error occurs, we can retry unless this is our final
                    # attempt, or the error code is a non-retryable one.
                    if (
                        final_retry
                        or ex.code() not in _RETRY_STATUS_CODES
                        or ex.code() in _additional_no_retry_status_codes
                    ):
                        raise ex
                    else:
                        failure_cause_msg = (
                            f"gRPC error occurred:"
                            f" (Status Code {ex.code()}) {ex.details()}"
                        )

                # If we reach this point we must be attempting a retry
                retry_count += 1

                # Backoff is increased using standard exponential backoff formula
                # For standard backoff factor of one this results in backoffs of
                # [1, 2, 4, 8, ...] seconds.
                backoff = backoff_factor * (2 ** (retry_count - 1))

                # Log out failure information and retry information.
                _logger.debug(
                    f"{failure_cause_msg}; "
                    f"will retry in {backoff} seconds (attempt {retry_count})."
                )

                await asyncio.sleep(backoff)

            # We shouldn't reach this point due to how the loop can be exited,
            # but just in case.
            raise BitfountMessageServiceError(
                "Unable to make connection, even after multiple attempts."
            )

        return cast(_F, _wrapped_async_grpc_func)

    if original_rpc_func:
        # Was used as @_auto_retry_grpc (or called directly).
        # original_rpc_func was passed in through the decorator machinery so just
        # wrap and return.
        return _decorate(original_rpc_func)
    else:
        # Was used as @_auto_retry_grpc(**kwargs).
        # original_rpc_func not yet passed in so need to return a decorator function
        # to allow the decorator machinery to pass it in.
        return _decorate
