import warnings

from .atomicpuppy import (
    Event,
    ExceptionCause,
    EventCounter,
    EventFinder as EventFinder_,
    EventPublisher,
    EventRaiser,
    EventStoreJsonEncoder,
    RedisCounter,
    StreamConfigReader,
    StreamFetcher,
    StreamReader,
    SubscriptionInfoStore,
)
from .errors import (
    FatalError,
    HttpClientError,
    HttpNotFoundError,
    HttpServerError,
    RejectedMessageException,
    StreamNotFoundError,
    UrlError,
)

import asyncio
import aiohttp


class EventFinder:

    def __init__(self, cfg_file, loop=None, username=None, password=None):
        """
        cfg_file: dictionary or filename or yaml text
        """
        if loop is not None:
            warnings.warn(
                "The loop parameter is unused and should be omitted",
                DeprecationWarning,
                stacklevel=2,
        )
        self._config = StreamConfigReader().read(cfg_file)
        self._session_auth = None
        if username != None and password != None:
            self._session_auth = aiohttp.BasicAuth(
                    login=username,
                    password=password,
                    encoding='utf-8')

    async def find_backwards(self, stream, predicate, predicate_label='predicate'):
        async with aiohttp.ClientSession(
                read_timeout=self._config.timeout,
                conn_timeout=self._config.timeout,
                raise_for_status=True,
                auth=self._session_auth) as session:

            instance_name = (
                self._config.instance_name + ' find_backwards {}'.format(stream)
            )
            fetcher = StreamFetcher(
                None, nosleep=False, max_time=self._config.max_time, session=session)
            head_uri = 'http://{}:{}/streams/{}/head/backward/{}'.format(
                self._config.host,
                self._config.port,
                stream,
                self._config.page_size)
            finder = EventFinder_(
                fetcher=fetcher,
                stream_name=stream,
                instance_name=instance_name,
                head_uri=head_uri,
            )
            result = await finder.find_backwards(stream, predicate, predicate_label)
            return result


class AtomicPuppy:

    def __init__(self, cfg_file, callback, loop=None, username=None, password=None):
        """
        cfg_file: dictionary or filename or yaml text
        """
        if loop is not None:
            warnings.warn(
                "The loop parameter is unused and should be omitted",
                DeprecationWarning,
                stacklevel=2,
        )
        self.config = StreamConfigReader().read(cfg_file)
        self.callback = callback
        self._queue = asyncio.Queue(maxsize=20)
        self._messageProcessor = None
        self._exception_handler = lambda exc, cause: None

        auth = None
        if username != None and password != None:
            auth = aiohttp.BasicAuth(login=username, password=password, encoding='utf-8')

        self.session = aiohttp.ClientSession(
                read_timeout=self.config.timeout,
                conn_timeout=self.config.timeout,
                raise_for_status=True,
                auth=auth)

    def set_exception_handler(self, handler):
        """Set exception handler function.

        The handler is called when either the counter or the application
        handler callback raises an otherwise unhandled exception.

        The handler should take two arguments: the first argument is the
        asyncio loop, and the second is a dictionary with the following keys:

        "exception": exception instance

        "atomicpuppy_cause": atomicpuppy.ExceptionCause instance indicating
        whether the exception was caused by updating the counter or running the
        application handler callback function.

        Note that this is similar to the .set_exception_handler of asyncio's
        loop, but not all of the keys defined by that function are currently
        included in the second argument dict.

        The exception handler is not currently called if .start() is called
        with run_once true.
        """
        self._exception_handler = handler
        if self._messageProcessor is not None:
            self._messageProcessor.set_exception_handler(handler)

    def start(self, run_once=False):
        c = self.counter = self.config.counter_factory()
        self._messageProcessor = EventRaiser(self._queue,
                                             c,
                                             self.callback,
                                             exception_handler=self._exception_handler)
        subscription_info_store = SubscriptionInfoStore(self.config, c)
        self.readers = [
            StreamReader(
                queue=self._queue,
                stream_name=s,
                instance_name=self.config.instance_name,
                max_time=self.config.max_time,
                subscriptions_store=subscription_info_store,
                session=self.session)
            for s in self.config.streams
        ]
        self.tasks = [s.start_consuming(once=run_once) for s in self.readers]
        if run_once:
            self.tasks.append(self._messageProcessor.consume_events())
        else:
            self.tasks.append(self._messageProcessor.start())
        return asyncio.gather(*self.tasks)

    def stop(self):
        self.session.close()
        for s in self.readers:
            s.stop()
        self._messageProcessor.stop()


__all__ = [
    AtomicPuppy,
    Event,
    EventCounter,
    EventFinder,
    EventPublisher,
    EventStoreJsonEncoder,
    FatalError,
    HttpClientError,
    HttpNotFoundError,
    HttpServerError,
    RedisCounter,
    RejectedMessageException,
    StreamNotFoundError,
    UrlError,
]
