from unittest import TestCase, main

from expects import expect, be, be_empty, equal, have_length
import requests
from twin_sister import open_dependency_context

from questions_three.http_client import HttpClient
from twin_sister.fakes import EndlessFake, MasterSpy


class FakeRequests(EndlessFake):

    def __init__(self, session_class=EndlessFake()):
        self.Session = session_class
        super().__init__()

    def __call__(self, *args, **kwargs):
        response = EndlessFake()
        response.status_code = 200
        return response


class TestCookies(TestCase):

    def setUp(self):
        self.context = open_dependency_context()
        self.session_class_spy = MasterSpy(FakeRequests())
        self.context.inject(requests, FakeRequests(
            session_class=self.session_class_spy))

    def tearDown(self):
        self.context.close()

    def test_cookies_disabled_by_default(self):
        HttpClient().get('http://spam')
        expect(self.session_class_spy.call_history).to(be_empty)

    def test_maintains_session_between_requests(self):
        client = HttpClient()
        client.enable_cookies()
        client.get('http://spam')
        client.get('http://eggs')
        expect(self.session_class_spy.call_history).to(have_length(1))

    def extract_prep_spy(self):
        session_spy = self.session_class_spy.return_value_spies[-1]
        return session_spy.attribute_spies['prepare_request']

    def extract_request_to_prep(self):
        spy = self.extract_prep_spy()
        args, kwargs = spy.call_history[-1]
        return args[0]

    def test_prepares_request_with_given_method(self):
        client = HttpClient()
        client.enable_cookies()
        client.delete('http://vikings')
        expect(self.extract_request_to_prep().method).to(equal('DELETE'))

    def test_prepares_request_with_given_url(self):
        client = HttpClient()
        client.enable_cookies()
        url = 'https://stuffed.io?first=who'
        client.get(url)
        expect(self.extract_request_to_prep().url).to(equal(url))

    def test_prepares_request_with_given_headers(self):
        client = HttpClient()
        client.enable_cookies()
        headers = {'spam': 'lovely', 'baked-beans': 'off'}
        client.get('http://menu', headers=headers)
        expect(self.extract_request_to_prep().headers).to(equal(headers))

    def test_prepares_request_with_given_data(self):
        client = HttpClient()
        client.enable_cookies()
        data = 'yaddayaddayadda'
        client.get('http://menu', data=data)
        expect(self.extract_request_to_prep().data).to(equal(data))

    def extract_send_spy(self):
        session_spy = self.session_class_spy.return_value_spies[-1]
        return session_spy.attribute_spies['send']

    def test_sends_prepared_request(self):
        client = HttpClient()
        client.enable_cookies()
        client.post('http://pewpewpew')
        prep_spy = self.extract_prep_spy()
        prepped = prep_spy.return_value_spies[-1]
        send_spy = self.extract_send_spy()
        args, kwargs = send_spy.call_history[-1]
        expect(args[0]).to(be(prepped))

    def test_returns_response(self):
        client = HttpClient()
        client.enable_cookies()
        response = client.head('http://pewpewpew')
        expect(response).to(equal(
            self.extract_send_spy().return_value_spies[-1]))


if '__main__' == __name__:
    main()
