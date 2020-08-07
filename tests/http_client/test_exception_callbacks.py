from functools import partial
from unittest import TestCase, main

from expects import expect, be, be_a
import requests
from twin_sister import open_dependency_context
from twin_sister.expects_matchers import raise_ex
from twin_sister.fakes import EndlessFake, FunctionSpy, func_that_raises

from questions_three.exceptions.http_error import HttpImATeapot, HttpNotFound, HttpUnauthorized
from questions_three.http_client import HttpClient
from questions_three.http_client.inspect_response import inspect_response


"""
As a component that uses the HttpClient and is aware of exceptions that may be raised with an HTTP response
I would like to instruct my HttpClient to handle the exception in a special way
So I don't need to add separate exception handling to each of my functions that uses the client.
"""


class Spam(RuntimeError):
    pass


class SonOfSpam(Spam):
    pass


class TestExeptionCallbacks(TestCase):
    def setUp(self):
        self.context = open_dependency_context()
        self.context.inject(requests, EndlessFake())

    def tearDown(self):
        self.context.close()

    def test_calls_callback_for_exception(self):
        exception_class = HttpUnauthorized
        spy = FunctionSpy()
        client = HttpClient()
        client.set_exceptional_response_callback(exception_class=HttpUnauthorized, callback=spy)
        self.context.inject(inspect_response, func_that_raises(exception_class()))
        try:
            client.get("http://spam")
        except exception_class:
            # This shouldn't be raised but this test doesn't care
            pass
        spy.assert_was_called()

    def test_passes_exception_as_kwarg(self):
        exception_class = HttpImATeapot
        spy = FunctionSpy(return_value=EndlessFake())
        client = HttpClient()
        client.set_exceptional_response_callback(exception_class=exception_class, callback=spy)
        self.context.inject(inspect_response, func_that_raises(exception_class()))
        client.get("http://foo.bar")
        expect(spy["exception"]).to(be_a(exception_class))

    def test_re_raises_unspecified_response_exception(self):
        client = HttpClient()
        client.set_exceptional_response_callback(exception_class=HttpNotFound, callback=lambda *a, **k: None)
        raised = HttpUnauthorized()
        self.context.inject(inspect_response, func_that_raises(raised))
        expect(partial(client.post, "http://mail.net")).to(raise_ex(raised))

    def test_calls_callback_for_child_class(self):
        specified_class = Spam
        raised_class = SonOfSpam
        spy = FunctionSpy()
        client = HttpClient()
        client.set_exceptional_response_callback(exception_class=specified_class, callback=spy)
        self.context.inject(inspect_response, func_that_raises(raised_class()))
        try:
            client.get("http://stuffed.com.au")
        except raised_class:
            # Exception should not be raised, but this test does not care
            pass
        spy.assert_was_called()

    def test_lets_exception_raised_by_callback_pass_through(self):
        exception_class = Spam
        raised = exception_class()
        callback = func_that_raises(raised)
        client = HttpClient()
        client.set_exceptional_response_callback(exception_class=HttpNotFound, callback=callback)
        self.context.inject(inspect_response, func_that_raises(HttpNotFound))
        expect(partial(client.put, "https://up.with.it")).to(raise_ex(raised))

    def test_rejects_parent_class_of_existing_key(self):
        client = HttpClient()
        client.set_exceptional_response_callback(exception_class=SonOfSpam, callback=EndlessFake())
        expect(partial(client.set_exceptional_response_callback, exception_class=Spam, callback=EndlessFake())).to(
            raise_ex(TypeError)
        )

    def test_rejects_child_class_of_existing_key(self):
        client = HttpClient()
        client.set_exceptional_response_callback(exception_class=Spam, callback=EndlessFake())
        expect(
            partial(client.set_exceptional_response_callback, exception_class=SonOfSpam, callback=EndlessFake())
        ).to(raise_ex(TypeError))

    def test_re_raises_exception_if_callback_returns_none(self):
        original = HttpImATeapot()
        self.context.inject(inspect_response, func_that_raises(original))
        client = HttpClient()
        client.set_exceptional_response_callback(exception_class=HttpImATeapot, callback=lambda *a, **k: None)
        expect(partial(client.delete, "http://nothing.new")).to(raise_ex(original))

    def test_returns_response_returned_by_callback(self):
        callback_response = EndlessFake()
        self.context.inject(inspect_response, func_that_raises(HttpNotFound()))
        client = HttpClient()
        client.set_exceptional_response_callback(
            exception_class=HttpNotFound, callback=lambda *a, **k: callback_response
        )
        expect(client.get("http://stuffed")).to(be(callback_response))


if "__main__" == __name__:
    main()
