from unittest import TestCase, main

from expects import expect, be
import requests
from twin_sister import open_dependency_context
from twin_sister.fakes import EmptyFake, FunctionSpy, MutableObject

from questions_three.http_client import HttpClient


class TestDisableRequests(TestCase):

    def setUp(self):
        self.context = open_dependency_context()
        self.spies = MutableObject()
        requests_stub = EmptyFake(pattern_obj=requests)
        response = requests.Response()
        response.status_code = 200
        for method in ('get', 'post', 'put', 'delete', 'head'):
            spy = FunctionSpy(return_value=response)
            setattr(self.spies, method, spy)
            setattr(requests_stub, method, spy)
        self.context.inject(requests, requests_stub)

    def tearDown(self):
        self.context.close()

    def test_disables_redirects_on_get(self):
        HttpClient().get('stuffed')
        expect(self.spies.get['allow_redirects']).to(be(False))

    def test_disables_redirects_on_post(self):
        HttpClient().post('raisin.bran')
        expect(self.spies.post['allow_redirects']).to(be(False))

    def test_disables_redirects_on_put(self):
        HttpClient().put('that.down')
        expect(self.spies.put['allow_redirects']).to(be(False))

    def test_disables_redirects_on_head(self):
        HttpClient().head('out')
        expect(self.spies.head['allow_redirects']).to(be(False))

    def test_disables_redirects_on_delete(self):
        HttpClient().delete('all.the.things')


if '__main__' == __name__:
    main()
