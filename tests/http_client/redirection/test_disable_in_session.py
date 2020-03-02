from unittest import TestCase, main

from expects import expect, be
import requests
from twin_sister import open_dependency_context
from twin_sister.fakes import EndlessFake, FunctionSpy

from questions_three.http_client import HttpClient


class TestDisableInSession(TestCase):

    def setUp(self):
        self.context = open_dependency_context()
        requests_stub = EndlessFake(pattern_obj=requests)
        session_stub = EndlessFake(pattern_obj=requests.sessions.Session())
        self.send_spy = FunctionSpy(return_value=EndlessFake())
        session_stub.send = self.send_spy
        requests_stub.Session = lambda *a, **k: session_stub
        self.context.inject(requests, requests_stub)

    def tearDown(self):
        self.context.close()

    def check_disables_redirect(self, method):
        client = HttpClient()
        client.enable_cookies()
        getattr(client, method)('http://something')
        expect(self.send_spy['allow_redirects']).to(be(False))

    def test_disables_redirects_on_get(self):
        self.check_disables_redirect('get')

    def test_disables_redirects_on_post(self):
        self.check_disables_redirect('post')

    def test_disables_redirects_on_put(self):
        self.check_disables_redirect('put')

    def test_disables_redirects_on_head(self):
        self.check_disables_redirect('head')

    def test_disables_redirects_on_delete(self):
        self.check_disables_redirect('delete')


if '__main__' == __name__:
    main()
