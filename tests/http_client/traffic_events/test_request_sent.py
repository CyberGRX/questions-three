from unittest import TestCase, main

from expects import expect, equal
import requests
from twin_sister import open_dependency_context
from twin_sister.fakes import EndlessFake

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.http_client import HttpClient


class TestRequestSent(TestCase):

    def setUp(self):
        self.context = open_dependency_context(
            supply_env=True, supply_logging=True)
        self.requests_stub = EndlessFake()
        self.context.inject(requests, self.requests_stub)

    def tearDown(self):
        self.context.close()
        EventBroker.reset()

    def test_publishes_http_method(self):
        called_method = 'put'
        published_method = None

        def subscriber(http_method, **kwargs):
            nonlocal published_method
            published_method = http_method

        EventBroker.subscribe(
            event=TestEvent.http_request_sent, func=subscriber)
        client = HttpClient()
        getattr(client, called_method)('https://upwith.it')
        expect(published_method).to(equal(called_method.upper()))

    def test_publishes_request_url(self):
        called_url = 'https://art-mart.net'
        published_url = None

        def subscriber(request_url, **kwargs):
            nonlocal published_url
            published_url = request_url

        EventBroker.subscribe(
            event=TestEvent.http_request_sent, func=subscriber)
        HttpClient().get(called_url)
        expect(published_url).to(equal(called_url))

    def test_publishes_request_headers(self):
        request_headers = {'spam': 'surprise', 'eggs': 'fear', 'beans': 0}
        published_headers = None

        def subscriber(request_headers, **kwargs):
            nonlocal published_headers
            published_headers = request_headers

        EventBroker.subscribe(
            event=TestEvent.http_request_sent, func=subscriber)
        HttpClient().post('https://blah.blah', headers=request_headers)
        expect(published_headers).to(equal(request_headers))

    def test_publishes_request_data(self):
        planted_data = 'blah blah blah blah blah'
        published_data = None

        def subscriber(request_data, **kwargs):
            nonlocal published_data
            published_data = request_data

        EventBroker.subscribe(
            event=TestEvent.http_request_sent, func=subscriber)
        HttpClient().post('https://blah.blah', data=planted_data)
        expect(published_data).to(equal(planted_data))

    def test_publishes_event_before_sending_the_request(self):

        event_published = False
        request_sent = False
        request_sent_before_event_published = False

        def stub_post(*args, **kwargs):
            nonlocal request_sent
            request_sent = True
            return EndlessFake()

        def mock_subscriber(**kwargs):
            nonlocal event_published
            nonlocal request_sent_before_event_published
            event_published = True
            request_sent_before_event_published = request_sent

        self.requests_stub.post = stub_post

        EventBroker.subscribe(
            event=TestEvent.http_request_sent, func=mock_subscriber)

        HttpClient().post('http://something')
        assert event_published, 'The event was not published'
        assert not request_sent_before_event_published, \
            'Thre request was sent before the event was published'
        assert request_sent, \
            'Request was not sent after the event was published'


if '__main__' == __name__:
    main()
