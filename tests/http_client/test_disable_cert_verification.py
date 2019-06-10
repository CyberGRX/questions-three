from unittest import TestCase, main

from expects import expect, have_keys
from questions_three.http_client import HttpClient
from twin_sister.fakes import EmptyFake, MasterSpy
import requests
from twin_sister import open_dependency_context


class TestDisableCertValidation(TestCase):

    def setUp(self):
        self.context = open_dependency_context(
            supply_env=True, supply_logging=True)

    def tearDown(self):
        self.context.close()

    def test_enabled_by_default(self):
        spy = MasterSpy(EmptyFake())
        self.context.inject(requests, spy)
        HttpClient().get('http://spam')
        args, kwargs = spy.last_call_to('get')
        expect(kwargs).to(have_keys(verify=True))

    def test_disabled_when_configured(self):
        spy = MasterSpy(EmptyFake())
        self.context.inject(requests, spy)
        self.context.set_env(HTTPS_VERIFY_CERTS='FAlSe')
        HttpClient().get('http://spam')
        args, kwargs = spy.last_call_to('get')
        expect(kwargs).to(have_keys(verify=False))

    def test_enabled_in_session_by_default(self):
        requests_stub = EmptyFake()
        self.context.inject(requests, requests_stub)
        spy = MasterSpy(EmptyFake())
        requests_stub.Session = lambda *a, **k: spy
        client = HttpClient()
        client.enable_cookies()
        client.get('http://spam')
        args, kwargs = spy.last_call_to('send')
        expect(kwargs).to(have_keys(verify=True))

    def test_disabled_in_session_when_configured(self):
        self.context.set_env(HTTPS_VERIFY_CERTS='FAlSe')
        requests_stub = EmptyFake()
        self.context.inject(requests, requests_stub)
        spy = MasterSpy(EmptyFake())
        requests_stub.Session = lambda *a, **k: spy
        client = HttpClient()
        client.enable_cookies()
        client.get('http://spam')
        args, kwargs = spy.last_call_to('send')
        expect(kwargs).to(have_keys(verify=False))


if '__main__' == __name__:
    main()
