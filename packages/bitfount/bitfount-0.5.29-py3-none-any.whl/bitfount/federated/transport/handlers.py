"""Callbacks and wrappers for async message service calls."""
from __future__ import annotations

import asyncio
import atexit
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import wraps
import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Collection,
    Final,
    Generator,
    Generic,
    Optional,
    Set,
    TypeVar,
    Union,
    cast,
)

if TYPE_CHECKING:
    from bitfount.federated.transport.base_transport import _BaseMailbox, Handler
    from bitfount.federated.transport.message_service import (
        _BitfountMessage,
        _BitfountMessageType,
    )

from asyncio.futures import Future as AsyncFuture
from concurrent.futures import Future as ConcurrentFuture
from threading import Lock as ThreadingLock

from bitfount.federated.logging import _get_federated_logger

logger = _get_federated_logger(__name__)

_PRIORITY_HANDLER_MAX_WORKERS: Final = 5

# Return type placeholder
R = TypeVar("R")


class _AsyncCallback(Generic[R]):
    """Async wrapper around a callback function.

    Allows us to `await` on the result of this callback. By overriding __call__
    the fact that we've wrapped the callback is transparent to the calling code.
    """

    def __init__(self, fn: Callable[[_BitfountMessage], R]):
        """Create a new AsyncCallback.

        Args:
            fn: the callback function to be wrapped.
        """
        self._fn = fn
        self._result_exists = asyncio.Event()
        self._result: R

    def __call__(self, message: _BitfountMessage) -> None:
        """Call the underlying (synchronous) callback function."""
        # Overriding __call__ allows us to transparently wrap the underlying
        # function call so that the call to the async callback looks just like
        # a normal call to the function itself.
        self._result = self._fn(message)
        self._result_exists.set()

    async def result(self, timeout: Optional[int] = None) -> R:
        """Asynchronously retrieve the result of the callback.

        Will (non-blockingly) wait on the callback to be called.

        Args:
            timeout: Timeout in seconds to await on the result. If not
                provided, will wait indefinitely. Optional.

        Returns:
            The return value of the callback.

        Raises:
            asyncio.TimeoutError: If timeout provided and result is not set within
                timeout seconds.
        """
        if timeout:
            await asyncio.wait_for(self._result_exists.wait(), timeout)
        else:
            await self._result_exists.wait()
        return self._result

    def reset(self) -> None:
        """Clears the result of the callback, allowing it to be re-used."""
        # We don't need to clear the actual result here as that's set before the
        # _result_exists is set.
        self._result_exists.clear()


def _simple_message_returner(x: _BitfountMessage) -> _BitfountMessage:
    """Simple callback that simply returns the message."""
    return x


def _get_message_awaitable() -> _AsyncCallback[_BitfountMessage]:
    """Returns an awaitable wrapper around message retrieval."""
    return _AsyncCallback(_simple_message_returner)


class _AsyncMultipleResponsesHandler:
    """Wraps multiple expected responses in a singular awaitable."""

    def __init__(
        self,
        handler: Handler,
        message_types: Union[_BitfountMessageType, Collection[_BitfountMessageType]],
        mailbox: _BaseMailbox,
        responders: Collection[str],
    ):
        """Creates a handler for multiple responses of a given type(s).

        When expecting multiple separate responses from a set of responders, this
        class will provide an awaitable that returns when either all expected responses
        have been received, or when a timeout is reached (in which case it returns
        the set of those who didn't respond).

        Each message is passed to the assigned handler and track is kept of those
        who have responded. The awaitable returned blocks asynchronously on all
        responses being received.

        Can be used as a context manager which ensures that all message type handlers
        are correctly attached and removed at the end of the usage.

        Args:
            handler: The async function to call for each received message.
            message_types: The message types to handle.
            mailbox: The mailbox where messages will be received.
            responders: The set of expected responders.
        """
        self._orig_handler = handler
        if not isinstance(message_types, Iterable):
            message_types = [message_types]
        self._message_types = message_types
        self._mailbox = mailbox
        self.responders = responders

        # Initialise to the full set of expected and remove them as they response.
        self._not_responded = set(responders)

        # Synchronization primitives for handling multiple responses coming in
        # simultaneously and for keeping track of when all responses have been received.
        self._lock = asyncio.Lock()
        self._responses_done = asyncio.Event()
        self._timeout_reached = False

    async def handler(self, message: _BitfountMessage) -> None:
        """An augmented handler for multiple responses.

        Wraps the supplied handler and tracks the expected responses.

        Args:
            message: The message to be processed.
        """
        # We want to wrap the supplied handler with additional logic to (a) avoid
        # multiple calls to the handler simultaneously which may mess with state,
        # and (b) to enable us to monitor when all responses have been received so
        # we can exit.

        # This lock prevents multiple calls to the handler at the same time
        async with self._lock:
            # This check prevents calls being processed after we have marked it
            # as done, for instance if timeout has occurred.
            if not self._responses_done.is_set():
                # We mark the responder as responded and handle cases where we
                # receive an unexpected response.
                try:
                    self._not_responded.remove(message.sender)
                except KeyError:
                    if message.sender in self.responders:
                        logger.error(
                            f"Received multiple responses from {message.sender}; "
                            f"only expecting one response per responder."
                        )
                    else:
                        logger.error(
                            f"Received unexpected response from {message.sender}; "
                            f"they were not in the list of expected responders."
                        )
                # Once marked as responded we can call the underlying handler and then
                # check whether all responses have been received.
                else:
                    # As this supports both sync and async handlers we need to
                    # process the result (which should be None, but could be a
                    # Coroutine returning None). As such, we comfortably call the
                    # handler and then simply await the result if needed.
                    handler_return = self._orig_handler(message)
                    if inspect.isawaitable(handler_return):
                        # Mypy needs some assurance, despite the above check
                        handler_return = cast(Awaitable[None], handler_return)
                        await handler_return

                    if len(self._not_responded) == 0:
                        self._responses_done.set()
            # Handle responses received after we're marked as done
            else:
                if self._timeout_reached:
                    logger.warning(
                        f"Message received after timeout reached; "
                        f"responder too slow, message will not be processed: {message}"
                    )
                else:
                    logger.warning(
                        f"Received unexpected message after all responses were "
                        f"accounted for: {message}"
                    )

    def __enter__(self) -> _AsyncMultipleResponsesHandler:
        self.setup_handlers()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.remove_handlers()

    def setup_handlers(self) -> None:
        """Setup the augmented handler for the supplied message types."""
        for message_type in self._message_types:
            self._mailbox.register_handler(message_type, self.handler)

    def remove_handlers(self) -> None:
        """Remove the augmented handler for the supplied message types."""
        for message_type in self._message_types:
            self._mailbox.delete_handler(message_type, self.handler)

    async def wait_for_responses(self, timeout: Optional[int] = None) -> Set[str]:
        """Waits for the set of responses to be handled.

        Each response is passed to the supplied (augmented) handler and this method
        will return once all responders have responded or until timeout is reached.

        Args:
            timeout: Optional. Timeout in seconds to wait for all responses to be
                received. If provided, any responders who failed to respond in time
                will be returned as a set.

        Returns:
            The set of responders who did not respond in time.
        """
        # Wait for all responses to have been received or
        # until the timeout expires (if provided).
        try:
            if timeout:
                await asyncio.wait_for(self._responses_done.wait(), timeout)
            else:
                await self._responses_done.wait()
        except asyncio.TimeoutError:
            self._timeout_reached = True
            # Acquiring the lock guarantees that no other responses are
            # _currently_ being processed (and hence we can set the event)
            async with self._lock:
                # Setting this stops other responses in the event loop from
                # being processed _later_.
                self._responses_done.set()

        # Will be empty if all responses received
        return self._not_responded


@dataclass(frozen=True)
class _TemporaryHandler:
    """A wrapper indicating that a handler is to be used only once."""

    handler: Handler


# Create a thread pool for executing high-priority handlers and register its
# shutdown method to be run on program exit.
# Also create a container to store pending futures and to allow us to cancel them
# in the case of a shutdown.
_priority_handler_thread_pool = ThreadPoolExecutor(
    max_workers=_PRIORITY_HANDLER_MAX_WORKERS, thread_name_prefix="priority-handler"
)
_priority_handler_futures: Set[ConcurrentFuture] = set()
_priority_handler_futures_lock: Final = ThreadingLock()


def _shutdown_priority_handler_thread_pool() -> None:
    """Shutdown handler to ensure thread pool shutdown."""
    # Shutdown thread pool (any running tasks may run until completion)
    _priority_handler_thread_pool.shutdown(wait=False)

    # Cancel all outstanding futures
    # NOTE: In Python 3.9+ we can use the built-in ThreadPoolExecutor.shutdown()
    #       method to also cancel futures.
    with _priority_handler_futures_lock:
        for f in _priority_handler_futures:
            f.cancel()


atexit.register(_shutdown_priority_handler_thread_pool)


def _concurrent_future_done(fut: ConcurrentFuture) -> None:
    """Callback function for removing futures from _priority_handler_futures."""
    # As the handler is finished we can remove it from the set of futures that we
    # need to consider for cancellation. We use `discard()` here as we don't care
    # if it's already been removed.
    with _priority_handler_futures_lock:
        _priority_handler_futures.discard(fut)


def _wrap_handler_with_lock(
    fn: Callable[[_BitfountMessage], R], lock: ThreadingLock
) -> Callable[[_BitfountMessage], R]:
    """Wraps the target callable in a lock acquisition."""

    @wraps(fn)
    def _wrapped(message: _BitfountMessage) -> R:
        with lock:
            return fn(message)

    return _wrapped


class _PriorityHandler(Generic[R]):
    """A handler that executes with priority by running in a separate thread."""

    def __init__(self, fn: Callable[[_BitfountMessage], R], set_exclusive: bool = True):
        """Create new priority handler.

        Args:
            fn: The underlying handler to wrap.
            set_exclusive: Whether the handler should only allow one running call
                at any given time.
        """
        # TODO: [BIT-2112] Add support for running async callables in the priority
        #       handler thread pool. This may simply be using `asyncio.run()` but
        #       special consideration will need to be given for how the per-thread
        #       event loops will interact.
        if asyncio.iscoroutinefunction(fn):
            raise TypeError(
                "Priority handlers must be synchronous functions or methods."
            )

        self._orig_fn = fn

        # The lock is managed in here because it needs to be passed into the calling
        # thread and to ensure that only a single call to this handler can be being
        # run at a time. This precludes us from having the lock external to the
        # handler (i.e. in the _HandlerRegister) without having to have a different
        # call signature for the handler (to allow the lock to be passed in).
        self._lock: Optional[ThreadingLock] = None
        self._fn = self._orig_fn
        if set_exclusive:
            self.set_exclusive()

        # These are used to monitor for the event result and allow us to await on it.
        # NOTE: asyncio.Event() is not thread safe, and so this should only be
        #       accessed from the _calling_ thread. AsyncFuture is not _inherently_
        #       thread safe, but because we create it by wrapping a ConcurrentFuture
        #       it is (as the thread itself interacts with the ConcurrentFuture,
        #       not the AsyncFuture directly).
        self._called = asyncio.Event()
        self._fut: AsyncFuture[R]

    def __call__(self, message: _BitfountMessage) -> None:
        """Call the underlying handler in a thread."""
        c_fut = _priority_handler_thread_pool.submit(self._fn, message)

        # Register the concurrent future for later shutdown cancellation if needed
        # and adds done_callback
        with _priority_handler_futures_lock:
            _priority_handler_futures.add(c_fut)
        c_fut.add_done_callback(_concurrent_future_done)

        self._fut = asyncio.wrap_future(c_fut)
        self._called.set()

    def set_exclusive(self) -> None:
        """Sets the handler so that only one instance can be running at a time.

        If handler is already marked as exclusive, does nothing.
        """
        if not self._lock:
            self._lock = ThreadingLock()
            self._fn = _wrap_handler_with_lock(self._orig_fn, self._lock)

    @property
    def lock(self) -> Optional[ThreadingLock]:
        """Get the underlying threading.Lock if presented.

        If exclusivity is set, will return the threading.Lock used to ensure this,
        otherwise None.
        """
        return self._lock

    async def _result(self) -> R:
        """Handles actual result retrieval."""
        # If handler not yet called, wait for that to occur
        await self._called.wait()

        # Then wait for handler to complete
        return await self._fut

    async def result(self, timeout: Optional[int] = None) -> R:
        """Asynchronously retrieve the result of the callback.

        Will (non-blockingly) wait on the callback to be called.

        Args:
            timeout: Timeout in seconds to await on the result. If not
                provided, will wait indefinitely. Optional.

        Returns:
            The return value of the callback.

        Raises:
            asyncio.TimeoutError: If timeout provided and result is not set within
                timeout seconds.
        """
        return await asyncio.wait_for(self._result(), timeout)

    def __await__(self) -> Generator[Any, None, R]:
        """Allows `await` functionality directly on the result of the handler."""
        return self.result().__await__()
