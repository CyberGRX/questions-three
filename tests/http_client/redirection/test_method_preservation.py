from unittest import TestCase, main

from expects import expect, equal
import requests
from twin_sister import open_dependency_context
from twin_sister.fakes import EndlessFake, MutableObject

from questions_three.http_client import HttpClient


class FakeRequestsMethod:

    def __init__(self):
        self.already_redirected = False
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        response = requests.Response()
        if self.already_redirected:
            response.status_code = 200
        else:
            response.status_code = 301
            response.headers['Location'] = 'spam'
            self.already_redirected = True
        return response


class TestMethodPreservation(TestCase):

    def setUp(self):
        self.context = open_dependency_context()
        self.spies = MutableObject()
        requests_stub = EndlessFake(pattern_obj=requests)
        for method in ('get', 'post', 'put', 'delete', 'head'):
            fake = FakeRequestsMethod()
            setattr(self.spies, method, fake)
            setattr(requests_stub, method, fake)
        self.context.inject(requests, requests_stub)

    def tearDown(self):
        self.context.close()

    def check_method(self, method):
        getattr(HttpClient(), method)('https://some-host')
        spy = getattr(self.spies, method)
        expect(spy.call_count).to(equal(2))

    def test_preserves_get(self):
        self.check_method('get')

    def test_preserves_post(self):
        self.check_method('post')

    def test_preserves_put(self):
        self.check_method('put')

    def test_preserves_delete(self):
        self.check_method('delete')

    def test_preserves_head(self):
        self.check_method('head')


if '__main__' == __name__:
    main()
