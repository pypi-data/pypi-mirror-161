"""Base mailbox classes for other mailbox classes to inherit from."""
import asyncio
from asyncio import CancelledError, Task
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass
import inspect
from typing import (
    Any,
    AsyncContextManager,
    AsyncGenerator,
    Awaitable,
    Callable,
    Coroutine,
    DefaultDict,
    Dict,
    Final,
    Iterable,
    List,
    Literal,
    Mapping,
    NamedTuple,
    Optional,
    TypeVar,
    Union,
    cast,
    overload,
)
import warnings

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from grpc import RpcError, StatusCode
import msgpack

from bitfount.federated.exceptions import (
    MessageHandlerNotFoundError,
    MessageRetrievalError,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.transport.handlers import _PriorityHandler, _TemporaryHandler
from bitfount.federated.transport.message_service import (
    _BitfountMessage,
    _BitfountMessageType,
    _MessageEncryption,
    _MessageService,
    msgpackext_decode,
    msgpackext_encode,
)

logger = _get_federated_logger(__name__)

SyncHandler = Callable[[_BitfountMessage], None]
AsyncHandler = Callable[[_BitfountMessage], Awaitable[None]]
NonPriorityHandler = Union[SyncHandler, AsyncHandler]
Handler = Union[NonPriorityHandler, _PriorityHandler]

HANDLER_BACKOFF_SECONDS: int = 30

# Additional types for handler registration storage
ANY_MESSAGE: Final = "ANY_MESSAGE"
_ExtendedMessageTypes = Union[_BitfountMessageType, Literal["ANY_MESSAGE"]]
# Registered handlers can additionally be of type _TemporaryHandler
_RegisterHandler = Union[Handler, _TemporaryHandler]
_HandlersDict = Dict[_RegisterHandler, Optional[asyncio.Lock]]


@asynccontextmanager
async def _asyncnullcontext() -> AsyncGenerator[None, None]:
    """Async version of contextlib.nullcontext()."""
    yield None


class _HandlerLockPair(NamedTuple):
    """Pair of handler and associated exclusivity lock."""

    handler: _RegisterHandler
    lock: Optional[asyncio.Lock]


class _HandlerRegistry:
    """Registry for message handlers."""

    def __init__(
        self,
        handlers: Optional[
            Mapping[_BitfountMessageType, Union[Handler, Iterable[Handler]]]
        ] = None,
    ) -> None:
        self._registry: DefaultDict[_ExtendedMessageTypes, _HandlersDict] = defaultdict(
            dict
        )
        if handlers:
            # Register supplied handlers
            for message_type, handlers_ in handlers.items():
                try:
                    # Assume iterable
                    for handler in cast(Iterable[Handler], handlers_):
                        # TODO: [BIT-1048] Revisit this and decide if _all_ messages
                        #       need to be exclusive in this way.
                        self.register_handler(message_type, handler, exclusive=True)
                except TypeError:
                    # Otherwise, register individual handler
                    self.register_handler(
                        message_type, cast(Handler, handlers_), exclusive=True
                    )

    def register_handler(
        self,
        message_type: _ExtendedMessageTypes,
        handler: _RegisterHandler,
        exclusive: bool = True,
    ) -> None:
        """Registers a handler for a specific message type.

        Args:
            message_type: The message type to register the handler for.
            handler: The handler.
            exclusive: Whether only a single instance of the handler can be running
                at a given time.
        """
        if exclusive:
            if isinstance(handler, _PriorityHandler):
                # The exclusivity locking is handled within the priority handler
                # instead
                lock = None
                handler.set_exclusive()
            else:
                lock = asyncio.Lock()
        else:
            lock = None

        self._registry[message_type][handler] = lock

    def delete_handler(
        self,
        message_type: _ExtendedMessageTypes,
        handler: _RegisterHandler,
    ) -> None:
        """Deletes a handler associated with the message type."""
        self._registry[message_type].pop(handler)  # avoids KeyError

    def delete_all_handlers(self, message_type: _ExtendedMessageTypes) -> None:
        """Deletes all handlers for a specific message type."""
        self._registry[message_type].clear()

    @overload
    def get_handlers(
        self, message_type: _BitfountMessageType, with_locks: Literal[True]
    ) -> List[_HandlerLockPair]:
        """Gets all handlers for a specific message type."""
        ...

    @overload
    def get_handlers(
        self, message_type: _ExtendedMessageTypes, with_locks: Literal[False] = ...
    ) -> List[_RegisterHandler]:
        """Gets all handlers for a specific message type."""
        ...

    def get_handlers(
        self, message_type: _ExtendedMessageTypes, with_locks: bool = False
    ) -> Union[List[_RegisterHandler], List[_HandlerLockPair]]:
        """Gets all handlers for a specific message type.

        If `with_locks` is True, returns a list of tuples of the handlers and their
        exclusivity locks if present.

        Will also return all ANY_MESSAGE handlers if the requested message type
        is not itself ANY_MESSAGE.

        Args:
            message_type: The message type to retrieve the handlers for.
            with_locks: Whether to include handlers' exclusivity locks.

        Returns:
            Either a list of handlers or a list of handler-lock tuples.
        """
        handlers: Union[List[_RegisterHandler], List[_HandlerLockPair]]
        if not with_locks:
            handlers = list(self._registry[message_type].keys())

            # If not explicitly ANY_MESSAGE, extend the retrieved ones with the
            # handlers in ANY_MESSAGE
            if message_type != ANY_MESSAGE:
                handlers.extend(self._registry[ANY_MESSAGE].keys())
        else:
            handlers = [
                _HandlerLockPair(k, v) for k, v in self._registry[message_type].items()
            ]

            # If not explicitly ANY_MESSAGE, extend the retrieved ones with the
            # handlers in ANY_MESSAGE
            if message_type != ANY_MESSAGE:
                handlers.extend(
                    _HandlerLockPair(k, v)
                    for k, v in self._registry[ANY_MESSAGE].items()
                )

        return handlers

    def get_lock(
        self,
        message_type: _ExtendedMessageTypes,
        handler: _RegisterHandler,
    ) -> Optional[asyncio.Lock]:
        """Returns the exclusivity lock for a given handler and message type.

        Returns:
            The exclusivity lock for the handler or None if no lock.

        Raises:
            KeyError: If handler is not associated with message type.
        """
        return self._registry[message_type][handler]


class _BaseMailbox:
    """The base mailbox class.

    Contains handlers and message service.

    Args:
        mailbox_id: the ID of the mailbox to monitor.
        message_service: underlying message service instance.
        handlers: an optional mapping of message types to handlers to initialise with.
    """

    def __init__(
        self,
        mailbox_id: str,
        message_service: _MessageService,
        handlers: Optional[
            Mapping[_BitfountMessageType, Union[Handler, Iterable[Handler]]]
        ] = None,
    ):
        self.mailbox_id = mailbox_id
        self.message_service = message_service

        self._handlers: _HandlerRegistry = _HandlerRegistry(handlers)

        # Only one call to listen_for_messages() should be allowed at a time.
        # Otherwise we run the risk of messages being pulled off of the mailbox
        # by a listener that doesn't have the right handlers. Each mailbox should
        # only need one listener as it runs indefinitely.
        self._listening_lock = asyncio.Lock()

        # To enable a smart back-off when no handler is found before reattempting
        # we introduce an event that can monitor when new handlers are added. This
        # allows us to handle the situation where a response comes through faster
        # than the correct handler can be attached.
        self._new_handler_added = asyncio.Event()

    async def log(self, message: Mapping[str, object]) -> None:
        """Log message to remote task participant."""
        raise NotImplementedError

    def _setup_federated_logging(self) -> None:
        """Sets up federated logging."""
        raise NotImplementedError

    async def listen_for_messages(self) -> None:
        """Listens for messages on the target mailbox.

        Received messages are passed to the relevant handlers. If no relevant
        handlers are found, it will wait for up to `HANDLER_BACKOFF_SECONDS`
        for one to be registered. This avoids the situation of a response coming
        through faster than a handler can be registered. If not, it is passed
        to the default handler.
        """
        # Guarantee that only one listener is listening at a time.
        async with self._listening_lock:
            try:
                async for message in self.message_service.poll_for_messages(
                    self.mailbox_id
                ):
                    try:
                        await self._handle_message(message)
                    except MessageHandlerNotFoundError:
                        self._default_handler(message)
            # General message service issues to log out before failing.
            except RpcError as err:
                if err.code() == StatusCode.UNAVAILABLE:
                    logger.warning("Message Service unavailable")
                if err.code() == StatusCode.UNAUTHENTICATED:
                    # This could be a temporary token expiry issue
                    logger.info(
                        f"Authentication to read from '{self.mailbox_id}' failed"
                    )
                if err.code() == StatusCode.PERMISSION_DENIED:
                    logger.warning(
                        f"You don't own a pod with the mailbox: {self.mailbox_id}. "
                        f"Ensure it exists on Bitfount Hub."
                    )
                if err.code() == StatusCode.FAILED_PRECONDITION:
                    logger.debug(
                        f"No mailbox exists for '{self.mailbox_id}', "
                        f"ensure connect_pod() or send_task_requests() is called first."
                    )
                raise MessageRetrievalError(
                    f"An error occurred when trying to communicate"
                    f" with the messaging service: {err}"
                )

    async def _handle_message(
        self, message: _BitfountMessage
    ) -> List[Union[Task, _PriorityHandler]]:
        """Finds and runs handler(s) for the supplied message.

        The lower-priority handler(s) (whether async or not) are run as
        asyncio.Tasks to avoid blocking listen_for_messages().

        High-priority handlers are run directly (although in actuality in a thread)
        to avoid a blocking async task from stopping them being executed.

        Args:
            message: The message to handle.

        Returns:
            The created asyncio.Tasks in which the handler(s) are being run or,
            for high-priority handlers, the _PriorityHandler which the execution
            is tied to.

        Raises:
            MessageHandlerNotFoundError: If no handler is registered for message
                                         type and one is not registered within
                                         the timeout.
        """
        message_type: _BitfountMessageType = message.message_type
        awaitables: List[Union[Task, _PriorityHandler]] = []

        # Try to find relevant handler(s) for this message type
        handlers: List[_RegisterHandler] = await self._retrieve_handlers(message_type)

        # We create an async wrapper around the handler call regardless of if it's
        # an async function or not to allow us to run it in the background as a Task.
        # This also allows us to access the asyncio.Locks.
        #
        # We need to use a separate method to return the wrapper (rather than defining
        # it in the for-loop) due to the late-binding of closures in Python.
        def _get_running_handler_wrapper(
            handler: NonPriorityHandler,
        ) -> Callable[[], Coroutine[None, None, None]]:
            async def _running_handler_wrapper() -> None:
                # Only a single handler instance (i.e. a call to a specific handler
                # function) should be running at a given time; this helps avoid
                # conflicting use of shared resources and ensures that tasks we
                # _want_ to block (such as worker running) do so.
                # TODO: [BIT-1048] Revisit this and decide if _all_ messages need to
                #       be exclusive in this way.
                message_lock: Optional[AsyncContextManager]
                try:
                    message_lock = self._handlers.get_lock(message_type, handler)
                except KeyError:
                    message_lock = None

                if message_lock is None:
                    message_lock = _asyncnullcontext()

                async with message_lock:
                    # As this supports both sync and async handlers we need to
                    # process the result (which should be None, but could be a
                    # Coroutine returning None). As such, we comfortably call the
                    # handler and then simply await the result if needed.
                    logger.debug(f"Handling {message.message_type} message")
                    result = handler(message)
                    if inspect.isawaitable(result):
                        # Mypy needs some assurance, despite the above check
                        result = cast(Awaitable[None], result)
                        await result

            return _running_handler_wrapper

        for handler_ in handlers:
            handler_callable: Handler
            if not isinstance(handler_, _TemporaryHandler):
                handler_callable = handler_
            else:
                handler_callable = handler_.handler

            if not isinstance(handler_callable, _PriorityHandler):
                # For non-priority handlers we wrap them in asyncio.Tasks and farm
                # them out to the event loop. We return the Task instance so it
                # can be monitored later.
                wrapped_handler = _get_running_handler_wrapper(handler_callable)
                awaitables.append(asyncio.create_task(wrapped_handler()))
            else:
                # The handler register locks aren't used for _PriorityHandler as
                # they get run in other threads and asyncio.Locks aren't thread
                # safe. The _PriorityHandler itself enforces locking.
                handler_callable(message)
                awaitables.append(handler_callable)

            # As handler has been dispatched, we should delete it if it's a
            # temporary handler
            if isinstance(handler_, _TemporaryHandler):
                logger.debug(
                    f"Temporary handler {handler_} has been dispatched."
                    f" Deleting handler."
                )
                self._delete_handler(message_type, handler_)

        return awaitables

    async def _retrieve_handlers(
        self, message_type: _BitfountMessageType, timeout: int = HANDLER_BACKOFF_SECONDS
    ) -> List[_RegisterHandler]:
        """Retrieve the registered handler(s) for the given message type.

        If no handler(s) are registered for message type, wait for up to `timeout`
        for one to be registered. Otherwise, raise KeyError.

        Args:
            message_type: Message type to retrieve handler for.
            timeout: Number of seconds to wait before declaring no handler found.

        Returns:
            The handler(s) registered for the given message type.

        Raises:
            MessageHandlerNotFoundError: If no handler is registered for message
                                         type and one is not registered within
                                         the timeout.
        """
        # If handler(s) are already registered, `_retrieve_handlers_backoff()` will
        # return them immediately. Otherwise, we wait for it to return for at most
        # `timeout` seconds before raising MessageHandlerNotFoundError.
        try:
            handlers = await asyncio.wait_for(
                self._retrieve_handlers_backoff(message_type),
                timeout=timeout,
            )
            return handlers
        except asyncio.TimeoutError as te:
            # This is only for debug purposes as the MessageHandlerNotFoundError
            # will be swallowed by the checks in listen_for_messages and the default
            # handler will be used to process the message.
            logger.debug(
                f"No handler found within backoff period "
                f"for message type {message_type}."
            )
            raise MessageHandlerNotFoundError from te

    async def _retrieve_handlers_backoff(
        self, message_type: _BitfountMessageType
    ) -> List[_RegisterHandler]:
        """Wait for handler(s) to be available for message type and return them."""
        # See if we have a relevant handler(s), try to return immediately
        try:
            # If no handlers registered, will return an empty list
            if handlers := self._handlers.get_handlers(message_type):
                return handlers
            else:
                raise KeyError(
                    f"No handlers registered for message type {message_type}"
                )
        except KeyError:
            # If not, loop indefinitely, waiting on handler registration events
            while True:
                # Wait for a new handler to be registered. If one is already registered
                # since the last time this backoff was attempted, returns immediately.
                await self._new_handler_added.wait()
                try:
                    # See if the newly registered handler is for the message type
                    # we are interested in.
                    # If no handlers registered, will return an empty list
                    if handlers := self._handlers.get_handlers(message_type):
                        return handlers
                    else:
                        raise KeyError(
                            f"No handlers registered for message type {message_type}"
                        )
                except KeyError:
                    # Clear the handler registration event so we can monitor when
                    # another handler is registered.
                    #
                    # We do this at the end of the iteration so that we avoid a race
                    # condition between when `_retrieve_handlers_backoff()` is called
                    # and when it is run where a handler could be registered in that
                    # gap. Clearing the event at the start of the iteration would mean
                    # that handler was missed.
                    #
                    # If it's not actually a "new" handler that caused the event to be
                    # set, this is not an issue as the try...catch will handle it.
                    self._new_handler_added.clear()

    def _register_handler(
        self, message_type: _ExtendedMessageTypes, handler: _RegisterHandler
    ) -> None:
        """Registers a handler for a specific message type."""
        self._handlers.register_handler(message_type, handler)

        # Note we've added a new handler, to allow backed off handler retrieval
        # to know.
        self._new_handler_added.set()

    def register_handler(
        self,
        message_type: _BitfountMessageType,
        handler: Handler,
        high_priority: bool = False,
    ) -> Handler:
        """Registers a handler for a specific message type.

        If `high_priority` is true, the handler will be converted to a high priority
        handler. Note that only synchronous functions are compatible with
        `high_priority`.

        Returns:
            The registered handler, which may not be the same as the supplied handler.
        """
        handler = self._process_handler(handler, high_priority)

        logger.debug(f"Registering handler {handler} for message type {message_type}")
        self._register_handler(message_type, handler)

        return handler

    def register_universal_handler(
        self, handler: Handler, high_priority: bool = False
    ) -> Handler:
        """Registers a universal handler, one that will be called for all messages.

        If `high_priority` is true, the handler will be converted to a high priority
        handler. Note that only synchronous functions are compatible with
        `high_priority`.

        Returns:
            The registered handler, which may not be the same as the supplied handler.
        """
        handler = self._process_handler(handler, high_priority)

        logger.debug(f"Registering universal handler {handler}")
        self._register_handler(ANY_MESSAGE, handler)

        return handler

    def register_temp_handler(
        self,
        message_type: _BitfountMessageType,
        handler: Handler,
        high_priority: bool = False,
    ) -> _TemporaryHandler:
        """Registers a handler that will be deleted after it is called.

        If `high_priority` is true, the handler will be converted to a high priority
        handler. Note that only synchronous functions are compatible with
        `high_priority`.

        Returns:
            The registered temporary handler.
        """
        handler = self._process_handler(handler, high_priority)
        temp_handler = self._make_temp_handler(handler)

        logger.debug(
            f"Registering temporary handler {handler} for message type {message_type}"
        )
        self._register_handler(message_type, temp_handler)

        return temp_handler

    def register_temp_universal_handler(
        self, handler: Handler, high_priority: bool = False
    ) -> _TemporaryHandler:
        """Registers a universal handler that will be deleted after it is called.

        If `high_priority` is true, the handler will be converted to a high priority
        handler. Note that only synchronous functions are compatible with
        `high_priority`.

        Returns:
            The registered temporary handler.
        """
        handler = self._process_handler(handler, high_priority)
        temp_handler = self._make_temp_handler(handler)

        logger.debug(f"Registering temporary universal handler {handler}")
        self._register_handler(ANY_MESSAGE, temp_handler)

        return temp_handler

    @staticmethod
    def _make_temp_handler(handler: Handler) -> _TemporaryHandler:
        """Wraps handler so that it will be deleted after it is called."""
        return _TemporaryHandler(handler)

    def _delete_handler(
        self, message_type: _BitfountMessageType, handler: _RegisterHandler
    ) -> None:
        """Delete a handler from the registry."""
        self._handlers.delete_handler(message_type, handler)

    def delete_handler(
        self,
        message_type: _BitfountMessageType,
        handler: Optional[_RegisterHandler] = None,
    ) -> None:
        """Deletes a handler associated with the message type.

        If a specific handler is not provided, deletes all handlers for that
        message type.
        """
        if not handler:
            warnings.warn(
                "In future versions, delete_handler will require a specific handler"
                " instance to be provided. Please switch to delete_all_handlers"
                " instead to maintain previous functionality.",
                DeprecationWarning,
            )
            self.delete_all_handlers(message_type)
        else:
            logger.debug(f"Deleting handler for message type: {message_type}")
            self._delete_handler(message_type, handler)

    def delete_universal_handler(self, handler: _RegisterHandler) -> None:
        """Deletes a specific universal handler."""
        logger.debug(f"Deleting universal handler {handler}")
        self._handlers.delete_handler(ANY_MESSAGE, handler)

    def delete_all_handlers(self, message_type: _BitfountMessageType) -> None:
        """Deletes all handlers for a specific message type."""
        logger.debug(f"Deleting all handlers for message type: {message_type}")
        self._handlers.delete_all_handlers(message_type)

    def delete_all_universal_handlers(self) -> None:
        """Deletes all universal handlers."""
        logger.debug("Deleting all universal handlers")
        self._handlers.delete_all_handlers(ANY_MESSAGE)

    @staticmethod
    def _default_handler(message: _BitfountMessage) -> None:
        """Simple default handler that logs the message details.

        If this is called it is because we have received a message type that we
        were not expecting and do not know how to handle. We log out pertinent
        (non-private) details.
        """
        logger.error(
            f"Received unexpected message "
            f"("
            f"type: {message.message_type}; "
            f"sender {message.sender}; "
            f"recipient {message.recipient}"
            f"). "
            f"Message was not handled."
        )

    @staticmethod
    def _process_handler(handler: Handler, high_priority: bool) -> Handler:
        """Process the supplied handler given handler configuration.

        Handles conversion into high priority handlers as needed and also does
        type-checking for supported handler types.

        Return:
            The processed (and hence potentially changed) handler.
        """
        if high_priority:
            if isinstance(handler, _PriorityHandler):
                # Already correct, just return
                return handler
            # TODO: [BIT-2112] Add support for running async callables in the priority
            #       handler thread pool. This may simply be using `asyncio.run()` but
            #       special consideration will need to be given for how the per-thread
            #       event loops will interact.
            elif asyncio.iscoroutinefunction(handler):
                raise TypeError(
                    "High priority is not compatible with async functions;"
                    " please provide a sync function."
                )
            else:
                logger.debug(f"Converting handler {handler} to high priority handler.")
                return _PriorityHandler(handler)
        else:
            if isinstance(handler, _PriorityHandler):
                logger.warning(
                    "A priority handler has been provided but high_priority not set."
                    " Treating as though high_priority is True."
                )
                return handler
            else:
                return handler


@dataclass
class _WorkerMailboxDetails:
    """Mailbox details for a specific task/worker on a pod.

    Attributes:
        pod_identifier: The parent pod's identifier.
        public_key: The parent pod's public key.
        mailbox_id: The mailbox ID for this specific task/worker.
        aes_encryption_key: The encryption key to use for this specific task/worker.
    """

    pod_identifier: str
    public_key: RSAPublicKey
    mailbox_id: str
    aes_encryption_key: bytes


# Type variable for return type below.
R = TypeVar("R")


async def _send_aes_encrypted_message(
    message: Any,
    aes_encryption_key: bytes,
    message_service: _MessageService,
    **kwargs: Any,
) -> None:
    """Packs message, encrypts it and sends it.

    Args:
        message: The message to be sent. Must support serialisation via msgpack.
        aes_encryption_key: Key used to encrypt message.
        message_service: The MessageService used to send the message.
        **kwargs: Keyword arguments passed to BitfountMessage constructor.
    """
    body = msgpack.dumps(message, default=msgpackext_encode)
    message_body = _MessageEncryption.encrypt_outgoing_message(body, aes_encryption_key)

    await message_service.send_message(
        _BitfountMessage(body=message_body, **kwargs),
        already_packed=True,
    )


def _decrypt_aes_message(message: _BitfountMessage, aes_encryption_key: bytes) -> Any:
    """Decrypt AES encrypted message.

    Args:
        message: Encrypted message to decrypt.
        aes_encryption_key: The AES key to use to decrypt.

    Returns:
        Decrypted message body.
    """
    body = _MessageEncryption.decrypt_incoming_message(message.body, aes_encryption_key)
    return msgpack.loads(body, ext_hook=msgpackext_decode)


async def _run_func_and_listen_to_mailbox(
    run_func: Coroutine[None, None, R],
    mailbox: _BaseMailbox,
) -> R:
    """Runs an async function and listens for messages simultaneously.

    This function allows any exceptions that occur in the run function or the
    listening method to be properly propagated to the calling code, which is not
    possible with a normal `asyncio.create_task()` wrapper.

    It also ensures that the mailbox.listen_for_messages() method is not run for
    longer than the lifetime of run_func.

    Args:
        run_func: The function to run that will be needing received messages.
        mailbox: The mailbox to use to listen for messages.

    Returns:
         The return value of run_func.
    """
    # Create a task for listening for messages. We do this first so the wrapper
    # can be aware of it.
    mailbox_listen_task: Task = asyncio.create_task(mailbox.listen_for_messages())

    # Create wrapper around function call so that it will cancel the mailbox
    # listening task once the run task is finished.
    async def run_func_wrapper() -> R:
        # Await the result of the provided coroutine.
        result = await run_func

        # As function is finished, cancel the mailbox from listening for messages.
        mailbox_listen_task.cancel()

        return result

    # Create a separate task for the wrapped function call
    run_task: Task = asyncio.create_task(run_func_wrapper())

    # Await on either the wrapped function call to finish (which will cause the
    # mailbox_listen_task to finish) or for one of them to throw an exception.
    # In that case we cancel both tasks (we won't know which one failed) and re-raise
    # the exception.
    try:
        await asyncio.gather(run_task, mailbox_listen_task, return_exceptions=False)
    except CancelledError:
        # This should be fine, and is likely just the mailbox_listen_task being
        # cancelled because the run task has finished, but we should log some info
        # out just in case.
        if run_task.cancelled():
            logger.debug("Run task was cancelled.")
        if mailbox_listen_task.cancelled():
            logger.debug("Mailbox listen_for_messages() task was cancelled.")
    except BaseException as ex:
        # This exception is re-raised down below, so it doesn't matter that this
        # clause is very broad. We want to capture even BaseExceptions to ensure
        # that we cancel the other task.
        if not isinstance(ex, asyncio.TimeoutError):
            logger.error("Exception encountered whilst waiting for run function")
            logger.exception(ex)
        else:
            # A TimeoutError is expected in the normal course of things so we don't
            # want to log it out. It is handled up the chain by the Pod before returning
            # to a graceful state. However we still want to cancel any associated tasks.
            logger.debug("TimeoutError encountered whilst waiting for run function")

        # Pass the exception into the other task so it can be notified
        other_task: Optional[Task] = None
        if not run_task.done():
            other_task = run_task
        elif not mailbox_listen_task.done():
            other_task = mailbox_listen_task

        if other_task:
            try:
                coro = other_task.get_coro()
                try:
                    # Assume that coro is a coroutine rather than an awaitable
                    coro = cast(Coroutine, coro)
                    coro.throw(ex)
                except AttributeError:
                    logger.warning(f"Unable to `throw()` exception into coro {coro}")
            except StopIteration:
                pass

        # Cancel both tasks if they're still running
        for task in [run_task, mailbox_listen_task]:
            try:
                task.cancel()
            except CancelledError:
                pass

        # Re-raise the initial exception
        raise ex

    # If no exceptions were thrown, return the result of the wrapped function call.
    run_result: R = run_task.result()
    return run_result
