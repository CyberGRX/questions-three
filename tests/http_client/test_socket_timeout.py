from unittest import TestCase, main

from expects import expect, equal
import requests
from twin_sister.expects_matchers import complain
from twin_sister.fakes import EndlessFake, FunctionSpy
from twin_sister import open_dependency_context

from questions_three.http_client import HttpClient


class TestSocketTimeout(TestCase):

    def setUp(self):
        self.context = open_dependency_context(
            supply_env=True, supply_logging=True)
        self.get_spy = FunctionSpy(return_value=EndlessFake())
        self.requests_stub = EndlessFake(pattern_obj=requests)
        self.requests_stub.get = self.get_spy
        self.context.inject(requests, self.requests_stub)

    def tearDown(self):
        self.context.close()

    def test_complains_if_timeout_non_numeric(self):
        self.context.set_env(HTTP_CLIENT_SOCKET_TIMEOUT='spam')
        expect(HttpClient).to(complain(TypeError))

    def test_does_not_set_timeout_if_not_configured(self):
        HttpClient().get('http://stuff')
        expect(self.get_spy['timeout']).to(equal(None))

    def test_does_not_set_timeout_if_empty_string(self):
        self.context.set_env(HTTP_CLIENT_SOCKET_TIMEOUT='')
        HttpClient().get('http://stuff')
        expect(self.get_spy['timeout']).to(equal(None))

    def test_sends_configured_timeout_for_plain_request(self):
        planted = 94.7
        self.context.set_env(HTTP_CLIENT_SOCKET_TIMEOUT=planted)
        HttpClient().get('http://things')
        expect(self.get_spy['timeout']).to(equal(planted))

    def test_sends_configured_timeout_for_session_request(self):
        planted = 37
        self.context.set_env(HTTP_CLIENT_SOCKET_TIMEOUT=planted)
        session_stub = EndlessFake()
        self.requests_stub.Session = lambda: session_stub
        send_spy = FunctionSpy(return_value=EndlessFake())
        session_stub.send = send_spy
        client = HttpClient()
        client.enable_cookies()
        client.get('http://truffles')
        expect(send_spy['timeout']).to(equal(planted))


if '__main__' == __name__:
    main()
