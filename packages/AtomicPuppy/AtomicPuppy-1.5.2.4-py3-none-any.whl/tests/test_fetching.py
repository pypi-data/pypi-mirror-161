import aiohttp
import asyncio
import logging
import os
from unittest.mock import patch
from uuid import UUID, uuid4

from atomicpuppy.atomicpuppy import (
    StreamReader, SubscriptionInfoStore, SubscriptionConfig
)
from atomicpuppy import EventFinder, StreamNotFoundError, HttpClientError
from .fakehttp import FakeHttp, SpyLog
from .fakes import FakeRedisCounter

from aiohttp.client import _RequestContextManager


SCRIPT_PATH = os.path.dirname(__file__)


class FakeRequestContext(_RequestContextManager):

    def __init__(self, coro):
        self.coro = coro

    async def __aenter__(self):
        self._resp = await self.coro
        print(self._resp)
        self._resp.raise_for_status()
        return self._resp


class FakeClientSession:

    def __init__(self, fake_http, username=None, password=None):
        self.http = fake_http
        self.closed = False
        if username is not None and password is not None:
            self.auth = username + password
        else:
            self.auth = None

    def get(self, uri, **kwargs):
        assert not self.closed

        return FakeRequestContext(self.http.respond(uri, self.auth))

    def close(self):
        self.closed = True

    async def __aenter__(self, *args):
        return self

    async def __aexit__(self, *args):
        self.close()


class EventFinderContext:

    def given_fake_http_and_an_event_loop(self):
        self.loop = asyncio.get_event_loop()
        self.http = FakeHttp()

    def make_and_run_finder(
            self,
            username=None,
            password=None,
            sought_event_type='other_event',
            stream_to_look_in='otherstream',
            expect_exceptions=()):
        config = {
            'streams': [],
            'host': self._host,
            'port': self._port,
            'instance': 'eventstore_reader',
            'page_size': 2
        }

        def predicate(evt):
            return evt.type == sought_event_type

        with patch('aiohttp.ClientSession') as mock:
            mock.return_value = FakeClientSession(self.http, username=username, password=password)
            finder = EventFinder({'atomicpuppy': config}, username, password)
            coro = finder.find_backwards(stream_to_look_in, predicate)
            self._log = SpyLog()
            with(self._log.capture()):
                try:
                    self.evt = self.loop.run_until_complete(coro)
                except expect_exceptions as exc:
                    self.exc = exc
            assert mock.return_value.closed


class When_we_find_an_event_in_a_stream_containing_multiple_events(
        EventFinderContext):

    _host = 'eventstore.local'
    _port = 2113

    def given_two_events_where_only_the_second_is_sought(self):
        head_uri = (
            'http://eventstore.local:2113/streams/otherstream/head/backward/2')
        stream = SCRIPT_PATH + '/responses/two-events-otherstream.json'
        self.http.registerJsonUri(head_uri, stream)
        self.http.registerErrorWhenRegisteredRequestsExhausted()

    def because_we_call_find_backwards(self):
        self.make_and_run_finder(sought_event_type='other_event')

    def it_should_fetch_the_first_matching_event(self):
        assert self.evt.stream == 'otherstream'
        assert self.evt.type == 'other_event'
        assert self.evt.data == {'spam': '1'}


class When_we_find_an_event_in_a_stream_with_two_pages(EventFinderContext):

    _host = 'localhost'
    _port = 2113

    def given_two_pages_where_the_sought_event_is_only_on_the_second(self):
        self.http.registerJsonUris({
            'http://localhost:2113/streams/more_spam_stream/head/backward/2':
              SCRIPT_PATH + '/responses/two-page-find-backwards/head.json',
            'http://localhost:2113/streams/more_spam_stream/0/backward/2':
              SCRIPT_PATH + '/responses/two-page-find-backwards/next.json',
        })
        self.http.registerErrorWhenRegisteredRequestsExhausted()

    def because_we_call_find_backwards(self):
        self.make_and_run_finder(
            sought_event_type='sought_event',
            stream_to_look_in='more_spam_stream')

    def it_should_fetch_the_first_matching_event(self):
        assert self.evt.stream == 'more_spam_stream'
        assert self.evt.type == 'sought_event'
        assert self.evt.data == {'spam': '1'}


class When_the_sought_event_is_not_there_two_pages(EventFinderContext):

    _host = 'localhost'
    _port = 2113

    def given_two_pages_where_the_sought_event_is_only_on_the_second(self):
        self.http.registerJsonUris({
            'http://localhost:2113/streams/more_spam_stream/head/backward/2':
              SCRIPT_PATH + '/responses/two-page-find-backwards/head.json',
            'http://localhost:2113/streams/more_spam_stream/0/backward/2':
              SCRIPT_PATH + '/responses/two-page-find-backwards/next.json',
        })
        self.http.registerErrorWhenRegisteredRequestsExhausted()

    def because_we_call_find_backwards(self):
        self.make_and_run_finder(
            sought_event_type='nonexistent_sought_event',
            stream_to_look_in='more_spam_stream')

    def it_should_return_None(self):
        assert self.evt is None

    def it_should_log_that_it_couldnt_be_found(self):
        for r in self._log._logs:
            print(r.msg)
        assert(any(r.msg.startswith("No matching event found")
                   and r.levelno == logging.WARNING
                   for r in self._log._logs))


class When_the_sought_event_is_not_there_one_page(EventFinderContext):

    _host = 'eventstore.local'
    _port = 2113

    def given_two_events_on_one_page(self):
        self.http.registerJsonUri(
            'http://eventstore.local:2113/streams/otherstream/head/backward/2',
            SCRIPT_PATH + '/responses/two-events-otherstream.json')
        self.http.registerErrorWhenRegisteredRequestsExhausted()

    def because_we_call_find_backwards(self):
        self.make_and_run_finder(
            sought_event_type='nonexistent_sought_event',
            stream_to_look_in='otherstream')

    def it_should_return_None(self):
        assert self.evt is None

    def it_should_log_that_it_couldnt_be_found(self):
        for r in self._log._logs:
            print(r.msg)
        assert(any(r.msg.startswith("No matching event found")
                   and r.levelno == logging.WARNING
                   for r in self._log._logs))


class When_the_sought_stream_is_not_there(EventFinderContext):

    _host = 'eventstore.local'
    _port = 2113

    def given_two_events_on_one_page(self):
        self.http.register404(
            'http://eventstore.local:2113/streams/otherstream/head/backward/2'
        )

    def because_we_call_find_backwards(self):
        self.make_and_run_finder(
            sought_event_type='nonexistent_sought_event',
            stream_to_look_in='otherstream',
            expect_exceptions=(StreamNotFoundError, ))

    def it_should_raise(self):
        assert isinstance(self.exc, StreamNotFoundError)

class When_we_pass_valid_credentials_to_the_sought_stream(EventFinderContext):

    _host = 'eventstore.local'
    _port = 2113

    def given_a_stream_with_two_events_and_credentials(self):
        head_uri = (
            'http://eventstore.local:2113/streams/otherstream/head/backward/2')
        stream = SCRIPT_PATH + '/responses/two-events-otherstream.json'
        self.http.registerServerCredentials('user', 'password')
        self.http.registerJsonUri(head_uri, stream)
        self.http.registerErrorWhenRegisteredRequestsExhausted()

    def because_we_provide_credentials_and_call_find_backwards(self):
        self.make_and_run_finder(
            sought_event_type='other_event',
            username='user',
            password='password')

    def it_should_fetch_the_first_matching_event(self):
        assert self.evt.stream == 'otherstream'
        assert self.evt.type == 'other_event'
        assert self.evt.data == {'spam': '1'}

class When_we_pass_invalid_credentials_to_the_sought_stream(EventFinderContext):

    _host = 'eventstore.local'
    _port = 2113

    def given_a_stream_with_two_events(self):
        head_uri = (
            'http://eventstore.local:2113/streams/otherstream/head/backward/2')
        stream = SCRIPT_PATH + '/responses/two-events-otherstream.json'
        self.http.registerServerCredentials('user', 'password')
        self.http.registerJsonUri(head_uri, stream)
        self.http.registerErrorWhenRegisteredRequestsExhausted()

    def because_we_provide_credentials_and_call_find_backwards(self):
        self.make_and_run_finder(
            sought_event_type='other_event',
            username='wronguser',
            password='wrongpassword',
            expect_exceptions=(HttpClientError, ))

    def it_should_raise_http_client_error(self):
        assert isinstance(self.exc, HttpClientError)


class StreamReaderContext:

    _loop = None
    _events = None
    _host = 'eventstore.local'
    _port = 2113

    def __init__(self):
        self.counter = FakeRedisCounter("test-instace-{}".format(uuid4()))

    def given_an_event_loop(self):
        self._log = SpyLog()
        self._loop = asyncio.get_event_loop()

        self.http = FakeHttp()
        self.session = FakeClientSession(self.http)
        self._queue = asyncio.Queue()

    def subscribe_and_run(self, stream, last_read=-1, max_time=60, nosleep=False):
        self._reader = self.subscribeTo(stream, last_read, max_time, nosleep)
        self.run_the_reader()

    def run_the_reader(self):
        with self._log.capture():
            self._loop.run_until_complete(
                self._reader.start_consuming(once=True)
            )

    def create_counter(self):
        return lambda: self.counter

    def subscribeTo(self, stream, last_read, max_time, nosleep=False):
        assert(last_read is not None)
        config = SubscriptionConfig(
            streams=None,
            counter_factory=self.create_counter,
            instance_name='foo',
            host=self._host,
            port=self._port,
            timeout=20,
            max_time=max_time,
            page_size=20)

        subscriptions_store = SubscriptionInfoStore(config, self.counter)
        if last_read != -1:
            self.counter[stream] = last_read
        self._reader = StreamReader(
            queue=self._queue,
            stream_name=stream,
            instance_name='foo',
            subscriptions_store=subscriptions_store,
            session=self.session,
            max_time=max_time,
            nosleep=nosleep)
        return self._reader


class When_a_stream_contains_a_single_event_and_the_counter_is_at_the_start(StreamReaderContext):

    _event = None

    @property
    def the_event(self):
        if(not self._event):
            self._event = self._queue.get_nowait()
        return self._event

    def given_a_feed_containing_one_event(self):
        self.http.registerJsonUri(
            'http://eventstore.local:2113/streams/newstream/0/forward/20',
            SCRIPT_PATH + '/responses/single-event.json')

    def because_we_start_the_reader(self):
        self.subscribe_and_run('newstream')

    def it_should_contain_the_body(self):
        assert(self.the_event.data == {"a": 1})

    def it_should_contain_the_event_type(self):
        assert(self.the_event.type == "my-event")

    def it_should_contain_the_event_id(self):
        assert(
            self.the_event.id == UUID('fbf4a1a1-b4a3-4dfe-a01f-ec52c34e16e4'))

    def it_should_contain_the_sequence_number(self):
        assert(self.the_event.sequence == 0)

    def it_should_contain_the_stream_id(self):
        assert(self.the_event.stream == "newstream")


class When_an_event_contains_no_data(StreamReaderContext):

    _event = None

    def given_a_feed_containing_one_event(self):
        self.http.registerJsonUri(
            'http://eventstore.local:2113/streams/newstream/0/forward/20',
            SCRIPT_PATH + '/responses/single-event-no-data.json')

    def because_we_start_the_reader(self):
        self._log = SpyLog()
        with(self._log.capture()):
            self.subscribe_and_run('newstream')

    def it_should_return_a_none_event(self):
        assert(self._queue.empty())

    def it_should_log_a_warning(self):
        for r in self._log._logs:
            print(r.msg)
        assert(any(r.msg.startswith("No `data` key found on event")
                   and r.levelno == logging.WARNING
                   for r in self._log._logs))


class When_an_event_contains_wrong_format_metadata(StreamReaderContext):

    _the_events = []

    def given_a_feed_containing_one_event(self):
        self.http.registerJsonUri(
            'http://eventstore.local:2113/streams/wrongmetadata/0/forward/20',
            SCRIPT_PATH + '/responses/single-event-with-wrong-format-metadata.json')

    def because_we_start_the_reader(self):
        self._log = SpyLog()
        with(self._log.capture()):
            self.subscribe_and_run('wrongmetadata')

    def it_should_return_one_event(self):
        assert len(self.the_events) == 1

    def it_should_log_a_warning(self):
        for r in self._log._logs:
            print(r.msg)
        assert(any(r.msg.startswith("Failed to parse json metaData")
                   and r.levelno == logging.WARNING
                   for r in self._log._logs))

    def the_event_should_contain_empty_dict_metadata(self):
        assert isinstance(self.the_events[0].metadata, dict)

    def the_event_link_metadata_should_none(self):
        assert self.the_events[0].link_metadata is None

    @property
    def the_events(self):
        if(not self._the_events):
            while(not self._queue.empty()):
                self._the_events.append(self._queue.get_nowait())

        return self._the_events


class When_an_event_contains_wrong_format_linkmetadata(StreamReaderContext):

    _the_events = []

    def given_a_feed_containing_one_event(self):
        self.http.registerJsonUri(
            'http://eventstore.local:2113/streams/wronglinkmetadata/0/forward/20',
            SCRIPT_PATH + '/responses/single-event-with-wrong-format-linkmetadata.json')

    def because_we_start_the_reader(self):
        self._log = SpyLog()
        with(self._log.capture()):
            self.subscribe_and_run('wronglinkmetadata')

    def it_should_return_one_event(self):
        assert len(self.the_events) == 1

    def the_event_should_contain_empty_dict_metadata(self):
        assert isinstance(self.the_events[0].metadata, dict)

    def the_event_link_metadata_should_none(self):
        assert self.the_events[0].link_metadata is None

    def it_should_log_a_warning(self):
        for r in self._log._logs:
            print(r.msg)
        assert(any(r.msg.startswith("Failed to parse json linkMetaData")
                   and r.levelno == logging.WARNING
                   for r in self._log._logs))

    @property
    def the_events(self):
        if(not self._the_events):
            while(not self._queue.empty()):
                self._the_events.append(self._queue.get_nowait())

        return self._the_events


class When_the_projected_events_contain_metadata(StreamReaderContext):

    _the_events = []

    def given_a_feed_containing_one_event(self):
        self.http.registerJsonUri(
            'http://eventstore.local:2113/streams/%24et-test-event/0/forward/20',
            SCRIPT_PATH + '/responses/multiple-events-on-projection-with-metadata.json')

    def because_we_start_the_reader(self):
        self._log = SpyLog()
        with(self._log.capture()):
            self.subscribe_and_run('%24et-test-event')

    def it_should_return_three_events(self):
        assert len(self.the_events) == 9

    def the_events_should_be_ordered_correctly(self):
        assert self.the_events[0].sequence == 0
        assert self.the_events[1].sequence == 1
        assert self.the_events[2].sequence == 2

    def the_events_should_contain_dict_metadata(self):
        assert isinstance(self.the_events[0].metadata, dict)

    def the_first_event_metadata_should_have_some_of_the_expected_fields(self):
        assert '$correlationId' in self.the_events[2].metadata
        assert 'raisedBy' in self.the_events[2].metadata
        assert 'timestamp' in self.the_events[2].metadata

    def the_events_should_have_correlation_id(self):
        assert self.the_events[3].correlation_id == '79339aa4-5aec-4de0-8afa-7e27511158ce'

    def the_events_should_stream(self):
        assert self.the_events[3].stream == '$et-test-event'

    def the_events_should_published_stream(self):
        assert self.the_events[3].published_stream == 'test-3f419d23-24dd-49b6-95b7-65467e0b48be'

    def the_events_should_published_sequence(self):
        assert self.the_events[3].published_sequence == 0

    def the_events_link_metadata_should_be_dict(self):
        assert isinstance(self.the_events[3].link_metadata, dict)

    def the_events_id_should_be_as_expected(self):
        assert self.the_events[3].id, 'ab6c6ca4-452b-47e6-8e02-bf253b0f434e'

    def the_events_link_metadata_should_be_as_expected(self):
        assert self.the_events[3].link_metadata["$causedBy"] == 'ab6c6ca4-452b-47e6-8e02-bf253b0f434e'

    @property
    def the_events(self):
        if(not self._the_events):
            while(not self._queue.empty()):
                self._the_events.append(self._queue.get_nowait())

        return self._the_events



class When_the_events_contain_metadata(StreamReaderContext):

    _the_events = []

    def given_a_feed_containing_one_event(self):
        self.http.registerJsonUri(
            'http://eventstore.local:2113/streams/test-0f6ffca0-e758-4289-824d-cade1c8a5c4f/0/forward/20',
            SCRIPT_PATH + '/responses/multiple-events-with-metadata.json')

    def because_we_start_the_reader(self):
        self._log = SpyLog()
        with(self._log.capture()):
            self.subscribe_and_run('test-0f6ffca0-e758-4289-824d-cade1c8a5c4f')

    def it_should_return_three_events(self):
        assert len(self.the_events) == 3

    def the_events_should_be_ordered_correctly(self):
        assert self.the_events[0].sequence == 0
        assert self.the_events[1].sequence == 1
        assert self.the_events[2].sequence == 2

    def the_events_should_contain_dict_metadata(self):
        assert isinstance(self.the_events[0].metadata, dict)

    def the_first_event_metadata_should_have_some_of_the_expected_fields(self):
        assert '$correlationId' in self.the_events[1].metadata
        assert 'raisedBy' in self.the_events[1].metadata
        assert 'timestamp' in self.the_events[1].metadata

    def the_events_should_have_correlation_id(self):
        assert self.the_events[1].correlation_id == '053c664a-b216-4a00-873d-546b5ada826b'

    def the_events_should_have_stream(self):
        assert self.the_events[1].stream == 'test-0f6ffca0-e758-4289-824d-cade1c8a5c4f'

    def the_events_should_have_published_stream(self):
        assert self.the_events[1].published_stream == 'test-0f6ffca0-e758-4289-824d-cade1c8a5c4f'

    def the_events_should_have_published_sequence(self):
        assert self.the_events[1].published_sequence == 1

    def the_event_id_should_be_as_expected(self):
        assert self.the_events[1].id, 'ec6f4aa5-cb47-4e5e-8088-6873da2f968a'

    def the_event_link_metadata_should_none(self):
        assert self.the_events[1].link_metadata is None

    @property
    def the_events(self):
        if(not self._the_events):
            while(not self._queue.empty()):
                self._the_events.append(self._queue.get_nowait())

        return self._the_events


class When_a_feed_contains_multiple_events(StreamReaderContext):

    _the_events = []

    def given_a_feed_containing_three_events(self):
        self.http.registerJsonUri('http://eventstore.local:2113/streams/foo/0/forward/20',
                                  SCRIPT_PATH + '/responses/three-events.json')

    def because_we_start_the_reader(self):
        self.subscribe_and_run('foo')

    def it_should_return_three_events(self):
        assert(len(self.the_events) == 3)

    def the_events_should_be_ordered_correctly(self):
        assert(self.the_events[0].sequence == 0)
        assert(self.the_events[1].sequence == 1)
        assert(self.the_events[2].sequence == 2)

    @property
    def the_events(self):
        if(not self._the_events):
            while(not self._queue.empty()):
                self._the_events.append(self._queue.get_nowait())

        return self._the_events


class When_a_last_read_event_is_specified(StreamReaderContext):

    _the_events = []

    def given_a_feed_containing_three_events(self):
        self.http.registerJsonUri('http://eventstore.local:2113/streams/foo/1/forward/20',
                                  SCRIPT_PATH + '/responses/three-events.json')
        self.http.registerJsonUri(
            'http://127.0.0.1:2113/streams/newstream2/3/forward/20',
            SCRIPT_PATH + '/responses/two-page/head_next_prev_prev.json')

    def because_we_start_the_reader(self):
        self.subscribe_and_run('foo', last_read=1)

    def it_should_return_one_event(self):
        assert(len(self.the_events) == 1)

    def the_events_should_be_ordered_correctly(self):
        assert(self.the_events[0].sequence == 2)

    @property
    def the_events(self):
        if(not self._the_events):
            while(not self._queue.empty()):
                self._the_events.append(self._queue.get_nowait())

        return self._the_events


class When_the_last_read_event_is_on_the_first_page(StreamReaderContext):

    _the_events = []

    def given_a_feed_spanning_two_pages(self):
        self._host = "127.0.0.1"

        self.http.registerJsonUris({
            'http://127.0.0.1:2113/streams/stock/80/forward/20':
            SCRIPT_PATH + '/responses/two-page/head.json',
            'http://127.0.0.1:2113/streams/stock/84/forward/20':
            SCRIPT_PATH + '/responses/two-page/head_next_prev_prev.json',


            })

    def because_we_start_the_reader(self):
        self.subscribe_and_run('stock', last_read=80)

    def we_should_raise_the_new_events(self):
        assert(len(self.the_events) == 3)

    def we_should_raise_the_events_in_the_correct_order(self):
        assert(self.the_events[0].sequence == 81)
        assert(self.the_events[2].sequence == 83)

    @property
    def the_events(self):
        if(not self._the_events):
            while(not self._queue.empty()):
                self._the_events.append(self._queue.get_nowait())

        return self._the_events


class When_the_reader_is_invoked_for_a_second_time(StreamReaderContext):

    _event = None

    @property
    def the_event(self):
        if(not self._event):
            self._event = self._queue.get_nowait()
        return self._event

    def given_a_reader_that_has_read_all_the_events(self):
        self.http.registerJsonUri(
            'http://eventstore.local:2113/streams/newstream/0/forward/20',
            SCRIPT_PATH + '/responses/single-event.json')
        self.http.registerJsonUri(
            'http://127.0.0.1:2113/streams/newstream/1/forward/20',
            SCRIPT_PATH + '/responses/empty.json')
        self.http.registerJsonUri(
            'http://eventstore.local:2113/streams/newstream/0/forward/20',
            SCRIPT_PATH + '/responses/single-event.json')
        self.http.registerJsonUri(
            'http://127.0.0.1:2113/streams/newstream/1/forward/20',
            SCRIPT_PATH + '/responses/empty.json')

        self.subscribe_and_run('newstream')
        self._queue.get_nowait()

    def because_we_run_the_reader_a_second_time(self):
        self.run_the_reader()

    def it_should_not_return_any_events(self):
        assert(self._queue.empty())

    def run_the_reader(self):
        mock = self.http.getMock()
        with patch("aiohttp.request", new=mock):
            self._loop.run_until_complete(
                self._reader.start_consuming(once=True)
            )


"""
In this context, we create a new stream containing a single event (head.json)
When we poll the stream a second time there are no new events, so we walk to the
previous link(head_prev.json, then head_prev2.json)

When we poll the stream a third time, there are 23 new events. Since that's more
than a page worth, we should first seek the last_read event on the next page
(head_prev2_next) then walk backward until we find a new empty page
(head_prev2_next_prev_prev.json)

"""


class When_events_are_added_after_the_first_run(StreamReaderContext):

    _the_events = []

    def given_a_changing_feed(self):
        # When we first hit the stream, it returns a single event
        self.http.registerJsonUri('http://eventstore.local:2113/streams/stock/0/forward/20',
                                  SCRIPT_PATH + '/responses/new-events/head.json')

        self.http.registerJsonUri('http://eventstore.local:2113/streams/stock/0/forward/20',
                                  SCRIPT_PATH + '/responses/new-events/head.json')

        self.http.registerJsonUri('http://eventstore.local:2113/streams/stock/0/forward/20',
                                  SCRIPT_PATH + '/responses/new-events/head.json')

        # On the second invocation, we receive no new events
        # On the third invocation, we receive two pages of two events each
        self.http.registerJsonsUri(
            'http://127.0.0.1:2113/streams/stock/85/forward/20',
            [SCRIPT_PATH + '/responses/new-events/head_prev.json',
             SCRIPT_PATH + '/responses/new-events/head_prev2.json',
             SCRIPT_PATH + '/responses/new-events/head_prev2.json', ])
        self.http.registerJsonUri(
            'http://127.0.0.1:2113/streams/stock/84/backward/20',
            SCRIPT_PATH + '/responses/new-events/head_prev2_next.json')
        self.http.registerJsonUri(
            'http://127.0.0.1:2113/streams/stock/105/forward/20',
            SCRIPT_PATH + '/responses/new-events/head_prev2_next_prev.json')
        self.http.registerJsonUri(
            'http://127.0.0.1:2113/streams/stock/108/forward/20',
            SCRIPT_PATH + '/responses/new-events/head_prev2_next_prev_prev.json')

    def because_we_run_the_reader_three_times(self):
        self._reader = self.subscribeTo('stock', -1, 60)
        self.run_the_reader()
        self.run_the_reader()
        self.run_the_reader()

    def it_should_have_read_all_the_events(self):
        assert(len(self.the_events) == 24)

    def it_should_have_read_the_events_in_the_correct_order(self):
        assert(self.the_events[0].sequence == 84)
        assert(self.the_events[23].sequence == 107)

    def run_the_reader(self):
        mock = self.http.getMock()
        with patch("aiohttp.request", new=mock):
            self._loop.run_until_complete(
                self._reader.start_consuming(once=True)
            )

    @property
    def the_events(self):
        if(not self._the_events):
            while(not self._queue.empty()):
                self._the_events.append(self._queue.get_nowait())

        return self._the_events


class When_reading_from_a_category_projection(StreamReaderContext):

    _the_events = []

    @property
    def the_events(self):
        if(not self._the_events):
            while(not self._queue.empty()):
                self._the_events.append(self._queue.get_nowait())

        return self._the_events

    def given_a_category_projection_stream(self):
        self.http.registerJsonUri(
            'http://eventstore.local:2113/streams/$ce-order/0/forward/20',
            SCRIPT_PATH + '/responses/category-projection/head.json'
        )

    def because_we_run_the_reader(self):
        self.subscribe_and_run('$ce-order')

    def it_should_have_read_all_the_events(self):
        assert len(self.the_events) == 3

    def it_should_have_read_the_events_in_the_correct_order(self):
        for seq in range(3):
            assert self.the_events[seq].sequence == seq

    def it_should_use_the_category_projection_stream_name(self):
        for seq in range(3):
            assert self.the_events[seq].stream == '$ce-order'


"""
Value errors pretty much mean that our URL is screwed, or that there's an SSL
context mismatch. In that case, we should just end the loop.
"""


class When_a_valueerror_occurs_during_fetch(StreamReaderContext):

    def given_a_malformed_uri(self):
        # This test used to create a broke URI but now we fake the
        # ClientSession so we need to explicitly raise the error
        self.http.registerCallbacksUri(
            'http://eventstore.local:2113/streams/my-stream/1/forward/20',
            [
                lambda: exec('raise ValueError()')
            ]
        )



    # note that we run with a real event loop, and don't explicitly
    # call stop. The exception will stop the loop.
    def because_we_start_the_reader(self):
        self._reader = self.subscribeTo("my-stream", 1, 60)
        with(self._log.capture()):
            self._loop.run_until_complete(
                self._reader.start_consuming()
                )

    def it_should_log_a_critical_error(self):
        assert(filter(lambda r: r.level == logging.CRITICAL, self._log._logs))


"""
If we get a client error, then something has gone wrong with the http
layer processing. It's almost certainly an intermittent fault and we should
retry.
"""


def fail_with_client_error():
    raise aiohttp.ClientOSError("Darn it, can't connect")


class When_a_client_error_occurs_during_fetch(StreamReaderContext):

    def given_a_client_error(self):
        self.http.registerCallbacksUri(
            'http://eventstore.local:2113/streams/newstream/0/forward/20',
            [
                fail_with_client_error,
                lambda: exec('raise ValueError()')
            ]
        )

    def because_we_start_the_reader(self):
        self.subscribe_and_run('newstream')

    def it_should_log_a_warning(self):
        for r in self._log._logs:
            print(r.msg)

        warnings = (r for r in self._log._logs if r.levelno == logging.WARNING)
        assert(any(log.msg == "Error occurred while requesting %s" for log in warnings))


class When_multiple_errors_of_the_same_type_occur(StreamReaderContext):

    def given_a_client_error(self):
        self.http.registerCallbacksUri(
            'http://eventstore.local:2113/streams/newstream/0/forward/20',
            [
                fail_with_client_error,
                fail_with_client_error,
                lambda: exec('raise ValueError()')
            ]
        )

    def because_we_start_the_reader(self):
        self.subscribe_and_run('newstream')

    def it_should_log_a_warning(self):
        for r in self._log._logs:
            print(r.msg)
        assert(len([r for r in self._log._logs if r.msg.startswith("Error occurred while requesting %s")]) == 1)


"""
If we get a disconnection error, then it's a network level issue. Retry with
a backoff.
"""


def fail_with_disconnected_error():
    raise aiohttp.ServerDisconnectedError("Darn it, can't connect")


class When_a_disconnection_error_occurs_during_fetch(StreamReaderContext):

    def given_a_disconnection_error(self):
        self.http.registerCallbacksUri(
            'http://eventstore.local:2113/streams/newstream/0/forward/20',
            [
                fail_with_disconnected_error,
                lambda: exec('raise ValueError()')
            ]
        )

    def because_we_start_the_reader(self):
        self.subscribe_and_run('newstream')

    def it_should_log_a_warning(self):
        assert(any(r.msg == "Error occurred while requesting %s"
                   and r.levelno == logging.WARNING
                   for r in self._log._logs))


def fail_with_timeout():
    raise asyncio.TimeoutError()


class When_a_timeout_error_occurs_during_fetch(StreamReaderContext):

    """
    If we get a Timeout error, then it's a network level issue. Retry with
    a backoff.
    """

    def given_a_timeout_error(self):
        self.http.registerCallbacksUri(
            'http://eventstore.local:2113/streams/newstream/0/forward/20',
            [
                fail_with_timeout,
                lambda: exec('raise ValueError()')
            ]
        )

    def because_we_start_the_reader(self):
        self.subscribe_and_run('newstream')

    def it_should_log_a_warning(self):
        assert(any(r.msg == "Error occurred while requesting %s"
                   and r.levelno == logging.WARNING
                   for r in self._log._logs))


"""
If we get a ClientResponseError error, then it's a network level issue. Retry with
a backoff.
"""


def fail_with_client_response_error():
    raise aiohttp.ClientResponseError(None, "Darn it, something went bad")


class When_a_client_response_error_occurs_during_fetch(StreamReaderContext):

    _log = SpyLog()

    def given_a_client_response_error(self):
        self.http.registerCallbacksUri(
            'http://eventstore.local:2113/streams/newstream/0/forward/20',
            [
                fail_with_client_response_error,
                lambda: exec('raise ValueError()')
            ]
        )

    def because_we_start_the_reader(self):
        self.subscribe_and_run('newstream')

    def it_should_log_a_warning(self):
        assert(any(r.msg == "Error occurred while requesting %s"
                   and r.levelno == logging.WARNING
                   for r in self._log._logs))


class When_a_max_time_is_exceeded(StreamReaderContext):

    _log = SpyLog()

    def given_a_disconnection_error(self):
        self.http.registerCallbacksUri(
            'http://eventstore.local:2113/streams/newstream/0/forward/20',
            [
                fail_with_disconnected_error,
                lambda: exec('raise ValueError()')
            ]
        )

    def because_we_start_the_reader(self):
        self.subscribe_and_run('newstream', max_time=1)

    def it_should_log_a_warning(self):
        assert(any(r.msg == "Error occurred while requesting %s"
                   and r.levelno == logging.WARNING
                   for r in self._log._logs))
        assert(any(r.msg == "Stream fetcher has failed to connect to eventstore at %s in the last %d attempts"
                   and r.levelno == logging.WARNING
                   for r in self._log._logs))


"""
If we get a 40x range message then something is wrong with our configuration,
we should stop the loop and log an error.
"""


class When_we_receive_a_4xx_range_error(StreamReaderContext):

    _log = SpyLog()

    def given_a_415(self):
        self.http.registerEmptyUri(
            'http://eventstore.local:2113/streams/newstream/0/forward/20', 415)

    def because_we_fetch_the_stream(self):
        self.subscribe_and_run('newstream')


    def it_should_log_an_error(self):
        assert(
            any(r.msg == "Received bad http response with status %d from %s"
                and r.levelno == logging.ERROR
                for r in self._log._logs))


class When_we_receive_a_404_range_error(StreamReaderContext):

    _log = SpyLog()

    def given_a_404(self):
        self.http.registerEmptyUri(
            'http://eventstore.local:2113/streams/newstream/0/forward/20', 404)
        self.http.registerCallbackUri(
                'http://eventstore.local:2113/streams/newstream/0/forward/20',
                lambda: exec('raise ValueError()'))

    def because_we_fetch_the_stream(self):
        self.subscribe_and_run('newstream')

    def it_should_log_an_exception(self):
        assert(
            any(r.msg == "Received bad http response with status %d from %s"
                and r.levelno == logging.ERROR
                for r in self._log._logs))


class When_we_receive_a_408_range_error(StreamReaderContext):

    _log = SpyLog()

    def given_a_408(self):
        self.http.registerEmptyUri(
            'http://eventstore.local:2113/streams/newstream/0/forward/20', 408)
        self.http.registerCallbackUri(
                'http://eventstore.local:2113/streams/newstream/0/forward/20',
                lambda: exec('raise ValueError()'))

    def because_we_fetch_the_stream(self):
        self.subscribe_and_run('newstream')

    def it_should_log_a_single_warning(self):
        assert(
            any(r.msg == "Error occurred while requesting %s"
                and r.levelno == logging.WARNING
                for r in self._log._logs))


"""
50x range error means that something has gone wonky with event store. Log an error
and retry with a backoff.
"""


class When_we_receive_a_50x_range_error(StreamReaderContext):

    def given_a_500(self):
        self.http.registerEmptyUri(
                'http://eventstore.local:2113/streams/newstream/0/forward/20', 500)
        self.http.registerCallbackUri(
                'http://eventstore.local:2113/streams/newstream/0/forward/20',
                lambda: exec('raise ValueError()'))

    def because_we_fetch_the_stream(self):
        self.subscribe_and_run("newstream")

    def it_should_log_a_single_warning(self):
        assert(
            any(r.msg == "Error occurred while requesting %s"
                and r.levelno == logging.WARNING
                for r in self._log._logs))


class When_an_event_has_bad_json(StreamReaderContext):

    _log = SpyLog()

    def given_a_feed_containing_one_event(self):
        self.http.registerJsonUri(
            'http://eventstore.local:2113/streams/newstream/0/forward/20',
            SCRIPT_PATH + '/responses/invalid-event.json')

    def because_we_start_the_reader(self):
        with(self._log.capture()):
            self.subscribe_and_run('newstream')

    def it_should_log_an_error(self):
        assert(any(
            r.msg == "Failed to parse json data for %s message %s"
            and r.levelno == logging.ERROR
            for r in self._log._logs))
