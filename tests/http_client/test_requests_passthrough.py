from unittest import TestCase, main

from expects import expect, equal
import requests
from twin_sister import open_dependency_context

from twin_sister.expects_matchers import contain_key_with_value, raise_ex
from questions_three.http_client import HttpClient
from twin_sister.fakes import EndlessFake, MasterSpy


class FakeResponse(EndlessFake):

    status_code = 200


class TestRequestsPassthrough(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True)
        self.requests_spy = MasterSpy(FakeResponse())
        self.context.inject(requests, self.requests_spy)

    def tearDown(self):
        self.context.close()

    def test_attribute_error_on_unknown_method(self):
        def attempt():
            HttpClient().this_method_does_not_exist

        expect(attempt).to(raise_ex(AttributeError))

    def check_request(self, method):
        url = "http://nothing"
        kwargs = {"spam": 42, "eggs": 0}
        getattr(HttpClient(), method)(url, **kwargs)
        req_args, req_kwargs = self.requests_spy.last_call_to(method)
        expect(req_args).to(equal((url,)))
        for k, v in kwargs.items():
            expect(req_kwargs).to(contain_key_with_value(k, v))

    def check_response(self, method):
        actual = getattr(HttpClient(), method)("http://something")
        spy = self.requests_spy.attribute_spies[method]
        expect(actual).to(equal(spy.return_value_spies[-1]))

    def test_delete_request(self):
        self.check_request("delete")

    def test_delete_response(self):
        self.check_response("delete")

    def test_get_request(self):
        self.check_request("get")

    def test_get_response(self):
        self.check_response("get")

    def test_head_request(self):
        self.check_request("head")

    def test_head_response(self):
        self.check_response("head")

    def test_options_request(self):
        self.check_request("options")

    def test_options_response(self):
        self.check_response("options")

    def test_patch_request(self):
        self.check_response("patch")

    def test_post_request(self):
        self.check_request("post")

    def test_post_response(self):
        self.check_response("post")

    def test_put_request(self):
        self.check_request("put")

    def test_put_response(self):
        self.check_response("put")


if "__main__" == __name__:
    main()
