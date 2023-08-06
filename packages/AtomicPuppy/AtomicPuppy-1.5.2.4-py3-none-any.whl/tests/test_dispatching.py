from types import SimpleNamespace as ns

import asyncio

from atomicpuppy import EventRaiser, RejectedMessageException, ExceptionCause
from atomicpuppy.atomicpuppy import Event
from .fakehttp import SpyLog
from uuid import uuid4


class When_an_event_is_processed:

    the_message = None
    event_recorder = {}
    sequence_no = 43

    def given_an_event_raiser(self):
        self._loop = asyncio.get_event_loop()
        self.message_id = uuid4()
        self.queue = asyncio.Queue()
        self.message_processor = EventRaiser(self.queue,
                                             self.event_recorder,
                                             lambda e: self.process_message(e))

    def because_we_add_a_message(self):
        msg = Event(self.message_id, "type", {}, "stream", self.sequence_no)
        asyncio.ensure_future(self.send_message(msg), loop=self._loop)
        self._loop.run_until_complete(self.message_processor.start())

    def it_should_have_sent_the_message(self):
        assert(self.the_message.id == self.message_id)

    def it_should_have_recorded_the_event(self):
        assert(self.event_recorder["stream"] == self.sequence_no)

    async def send_message(self, e):
        return await self.queue.put(e)

    def process_message(self, e):
        self.the_message = e
        self.message_processor.stop()


class When_an_event_is_processed_by_running_once:

    the_message = None
    event_recorder = {}
    sequence_no = 43

    def given_an_event_raiser(self):
        self._loop = asyncio.get_event_loop()
        self.message_id = uuid4()
        self.queue = asyncio.Queue()
        self.message_processor = EventRaiser(self.queue,
                                             self.event_recorder,
                                             lambda e: self.process_message(e))

    def because_we_add_a_message(self):
        msg = Event(self.message_id, "type", {}, "stream", self.sequence_no)
        asyncio.ensure_future(self.send_message(msg), loop=self._loop)
        self._loop.run_until_complete(self.message_processor.consume_events())

    def it_should_have_sent_the_message(self):
        assert(self.the_message.id == self.message_id)

    def it_should_have_recorded_the_event(self):
        assert(self.event_recorder["stream"] == self.sequence_no)

    async def send_message(self, e):
        return await self.queue.put(e)

    def process_message(self, e):
        self.the_message = e


class When_a_message_is_rejected:

    event_recorder = {}

    def given_an_event_raiser(self):
        self._log = SpyLog()
        self._loop = asyncio.get_event_loop()
        self.message_id = uuid4()
        self.queue = asyncio.Queue()

        self.event_raiser = EventRaiser(
            self.queue,
            self.event_recorder,
            lambda e: self.process_message(e),
        )

    def because_we_process_a_message(self):
        with(self._log.capture()):
            msg = Event(self.message_id, "message-type", {}, "stream", 2)
            asyncio.ensure_future(self.send_message(msg), loop=self._loop)
            self._loop.run_until_complete(self.event_raiser.start())

    def it_should_log_a_warning(self):
        m = "message-type message "+str(self.message_id) \
            +" was rejected and has not been processed"
        assert(any(r.message == m for r in self._log.warnings))

    def process_message(self, e):
        self.event_raiser.stop()
        raise RejectedMessageException()

    async def send_message(self, e):
        return await self.queue.put(e)


class When_a_message_raises_an_unhandled_exception:

    event_recorder = {}

    @classmethod
    def examples(cls):
        return [
            ns(use_exception_handler=False),
            ns(use_exception_handler=True),
        ]

    def given_an_event_raiser(self, example):
        self.example = example
        self._log = SpyLog()
        self._loop = asyncio.get_event_loop()
        self.message_id = uuid4()
        self.queue = asyncio.Queue()
        self.exc_handler_context = None
        self.exc_handler_loop = None

        if example.use_exception_handler:
            def exception_handler(context):
                self.exc_handler_context = context
        else:
            exception_handler = None

        self.event_raiser = EventRaiser(
            self.queue,
            self.event_recorder,
            lambda e: self.process_message(e),
            exception_handler=exception_handler
        )

    def because_we_process_a_message(self):
        with(self._log.capture()):
            msg = Event(self.message_id, "message-type", {}, "stream", 2)
            asyncio.ensure_future(self.send_message(msg))
            self._loop.run_until_complete(self.event_raiser.start())

    def it_should_log_an_error(self):
        if self.example.use_exception_handler:
            return

        m = "Failed to process message "
        assert(any(r.message.startswith(m) for r in self._log.errors))

    def it_should_call_the_exception_handler(self):
        if not self.example.use_exception_handler:
            return

        assert list(self.exc_handler_context.keys()) == \
            ["exception", "atomicpuppy_cause", "atomicpuppy_message"], \
            self.exc_handler_context
        assert isinstance(self.exc_handler_context["exception"],
                          NotImplementedError), \
                          self.exc_handler_context
        assert (self.exc_handler_context["atomicpuppy_cause"] ==
                ExceptionCause.handler), \
                self.exc_handler_context
        assert isinstance(
            self.exc_handler_context["atomicpuppy_message"], Event), \
            self.exc_handler_context

    def process_message(self, e):
        self.event_raiser.stop()
        raise NotImplementedError("This handler is not here")

    async def send_message(self, e):
        return await self.queue.put(e)


class When_the_callback_is_asynchronous:

    def given_an_event_raiser(self):
        self._log = SpyLog()
        self._loop = asyncio.get_event_loop()
        self.message_id = uuid4()
        self.queue = asyncio.Queue()
        events = {}
        self.callback_exhausted = [False]

        async def async_callback(evt):
            self.event_raiser.stop()
            self.callback_exhausted[0] = True

        self.event_raiser = EventRaiser(
            queue=self.queue,
            counter=events,
            callback=async_callback,
        )

    async def send_message(self, e):
        return await self.queue.put(e)

    def because_we_process_a_message(self):
        with(self._log.capture()):
            msg = Event(self.message_id, "message-type", {}, "stream", 2)
            asyncio.ensure_future(self.send_message(msg))
            self._loop.run_until_complete(self.event_raiser.start())

    def it_should_have_exhausted_the_callback(self):
        assert self.callback_exhausted[0]


class When_an_asynchronous_callback_fails:

    @classmethod
    def examples(cls):
        return [
            ns(use_exception_handler=False),
            ns(use_exception_handler=True),
        ]

    def given_an_event_raiser(self, example):
        self.example = example
        self._log = SpyLog()
        self._loop = asyncio.get_event_loop()
        self.message_id = uuid4()
        self.queue = asyncio.Queue()
        events = {}
        self.callback_exhausted = [False]

        class Failure(Exception):
            pass

        self.failure_type = Failure

        if example.use_exception_handler:
            def exception_handler(context):
                self.exc_handler_context = context
        else:
            exception_handler = None

        async def async_callback(evt):
            self.event_raiser.stop()
            raise Failure()

        self.event_raiser = EventRaiser(
            queue=self.queue,
            counter=events,
            callback=async_callback,
            exception_handler=exception_handler
        )

    async def send_message(self, e):
        return await self.queue.put(e)

    def because_we_process_a_message(self):
        with(self._log.capture()):
            msg = Event(self.message_id, "message-type", {}, "stream", 2)
            asyncio.ensure_future(self.send_message(msg))
            self._loop.run_until_complete(self.event_raiser.start())

    def the_exception_should_be_logged(self):
        if self.example.use_exception_handler:
            return

        m = "Failed to process message "
        assert(any(r.message.startswith(m) for r in self._log.errors))

    def it_should_call_the_exception_handler(self):
        if not self.example.use_exception_handler:
            return

        assert list(self.exc_handler_context.keys()) == \
            ["exception", "atomicpuppy_cause", "atomicpuppy_message"], \
            self.exc_handler_context
        assert isinstance(self.exc_handler_context["exception"],
                          self.failure_type), \
                          self.exc_handler_context
        assert (self.exc_handler_context["atomicpuppy_cause"] ==
                ExceptionCause.handler), \
                self.exc_handler_context
        assert isinstance(
            self.exc_handler_context["atomicpuppy_message"], Event), \
            self.exc_handler_context


class When_the_counter_raises_an_unhandled_exception:

    @classmethod
    def examples(cls):
        return [
            ns(use_exception_handler=False),
            ns(use_exception_handler=True),
        ]

    def given_an_event_raiser(self, example):
        self.example = example
        self._log = SpyLog()
        self._loop = asyncio.get_event_loop()
        self.message_id = uuid4()
        self.queue = asyncio.Queue()
        self.exc_handler_context = None

        if example.use_exception_handler:
            def exception_handler(context):
                self.exc_handler_context = context
        else:
            exception_handler = None

        class FailingCounter:
            def __setitem__(self, name, value):
                raise NotImplementedError()

        self.event_raiser = EventRaiser(
            self.queue,
            FailingCounter(),
            lambda e: self.process_message(e),
            exception_handler=exception_handler
        )

    def because_we_process_a_message(self):
        with(self._log.capture()):
            msg = Event(self.message_id, "message-type", {}, "stream", 2)
            asyncio.ensure_future(self.send_message(msg))
            self._loop.run_until_complete(self.event_raiser.start())

    def it_should_have_attempted_to_process_the_message(self):
        assert(self.the_message.id == self.message_id), self.the_message

    def it_should_log_an_error(self):
        if self.example.use_exception_handler:
            return

        m = "Failed to persist last read event with "
        assert(any(r.message.startswith(m) for r in self._log.errors))

    def it_should_call_the_exception_handler(self):
        if not self.example.use_exception_handler:
            return

        assert list(self.exc_handler_context.keys()) == \
            ["exception", "atomicpuppy_cause"], \
            self.exc_handler_context
        assert isinstance(self.exc_handler_context["exception"],
                          NotImplementedError), \
                          self.exc_handler_context
        assert (self.exc_handler_context["atomicpuppy_cause"] ==
                ExceptionCause.counter), \
                self.exc_handler_context

    def process_message(self, e):
        self.the_message = e
        self.event_raiser.stop()

    async def send_message(self, e):
        return await self.queue.put(e)
