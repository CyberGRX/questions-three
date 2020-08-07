from unittest import TestCase, main
import uuid

from expects import expect, be_a, equal
import requests
from twin_sister import open_dependency_context
from twin_sister.fakes import EndlessFake

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.http_client import HttpClient


class TestRequestUuid(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_logging=True)
        self.context.inject(requests, EndlessFake())

    def tearDown(self):
        self.context.close()

    def test_request_uuid_is_a_uuid(self):
        published_uuid = None

        def subscriber(request_uuid, **kwargs):
            nonlocal published_uuid
            published_uuid = request_uuid

        EventBroker.subscribe(event=TestEvent.http_request_sent, func=subscriber)
        HttpClient().get("http://spam.spam")
        expect(published_uuid).to(be_a(uuid.UUID))

    def test_request_uuid_is_same_in_request_event_and_response_event(self):
        class UuidCatcher:
            def __init__(self):
                self.uuid = None

            def __call__(self, request_uuid, **kwargs):
                self.uuid = request_uuid

        request_event_catcher = UuidCatcher()
        response_event_catcher = UuidCatcher()
        EventBroker.subscribe(event=TestEvent.http_request_sent, func=request_event_catcher)
        EventBroker.subscribe(event=TestEvent.http_response_received, func=response_event_catcher)
        HttpClient().get("http://stuff")
        expect(request_event_catcher.uuid).to(equal(response_event_catcher.uuid))


if "__main__" == __name__:
    main()
