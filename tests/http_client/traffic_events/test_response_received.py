from unittest import TestCase, main

from expects import expect, be
import requests
from twin_sister import open_dependency_context
from twin_sister.fakes import EndlessFake

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.http_client import HttpClient


class TestResponseReceived(TestCase):

    def setUp(self):
        self.context = open_dependency_context(
            supply_env=True, supply_logging=True)

    def tearDown(self):
        self.context.close()

    def test_publishes_response_object(self):
        planted_response = EndlessFake()
        published_response = None

        def subscriber(response, **kwargs):
            nonlocal published_response
            published_response = response

        requests_stub = EndlessFake()
        requests_stub.post = lambda *a, **k: planted_response
        self.context.inject(requests, requests_stub)
        EventBroker.subscribe(
            event=TestEvent.http_response_received,
            func=subscriber)
        HttpClient().post('http://something')
        expect(published_response).to(be(planted_response))


if '__main__' == __name__:
    main()
