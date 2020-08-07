from unittest import TestCase, main

from expects import expect
import requests
from twin_sister import open_dependency_context

from twin_sister.expects_matchers import contain_key_with_value
from questions_three.http_client import HttpClient
from twin_sister.fakes import EndlessFake, MasterSpy


class FakeRequests(EndlessFake):
    def __init__(self, session=EndlessFake()):
        self.status_code = 200
        self._session = session

    def Session(self, *args, **kwargs):
        return self._session

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        return self


class TestProxy(TestCase):
    """
    Requests 2.18.4 observes $HTTP_PROXY for basic requests
    but ignores them for session requests.

    HttpClient addresses this by forcing observance everywhere.
    """

    def setUp(self):
        self.context = open_dependency_context(supply_env=True)
        self.http_proxy = "http://munchausen-gateway:4427"
        self.https_proxy = "http://special-something:7727"
        self.context.os.environ = {"HTTP_PROXY": self.http_proxy, "HTTPS_PROXY": self.https_proxy}
        self.session_spy = MasterSpy(FakeRequests())
        self.requests_spy = MasterSpy(FakeRequests(self.session_spy))
        self.context.inject(requests, self.requests_spy)

    def tearDown(self):
        self.context.close()

    def test_plain_from_environment(self):
        HttpClient().get("http://yadda")
        spy = self.requests_spy.attribute_spies["get"]
        args, kwargs = spy.call_history[-1]
        expect(kwargs).to(contain_key_with_value("proxies", {"http": self.http_proxy, "https": self.https_proxy}))

    def test_plain_from_call(self):
        expected = "TERRIFIC CAN OF SPAM"
        HttpClient().get("http://whatever", proxies=expected)
        spy = self.requests_spy.attribute_spies["get"]
        args, kwargs = spy.call_history[-1]
        expect(kwargs).to(contain_key_with_value("proxies", expected))

    def test_session_from_environment(self):
        client = HttpClient()
        client.enable_cookies()
        client.post("http://something")
        spy = self.session_spy.attribute_spies["send"]
        args, kwargs = spy.call_history[-1]
        expect(kwargs).to(contain_key_with_value("proxies", {"http": self.http_proxy, "https": self.https_proxy}))

    def test_session_from_call(self):
        expected = "an halibut"
        client = HttpClient()
        client.enable_cookies()
        client.delete("http://nothing-to.see/here", proxies=expected)
        spy = self.session_spy.attribute_spies["send"]
        args, kwargs = spy.call_history[-1]
        expect(kwargs).to(contain_key_with_value("proxies", expected))


if "__main__" == __name__:
    main()
