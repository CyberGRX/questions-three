from unittest import TestCase, main
from urllib.parse import urlparse

from expects import expect, have_keys, equal
import requests
from twin_sister import open_dependency_context
from twin_sister.expects_matchers import complain
from twin_sister.fakes import EmptyFake, MutableObject

from questions_three.exceptions import InvalidHttpResponse, TooManyRedirects
from questions_three.exceptions.http_error import HttpUseProxy
from questions_three.http_client import HttpClient
from questions_three.vanilla import url_append


class FakeRequestsMethod:

    def __init__(self, responses):
        self.call_history = []
        self.responses = responses

    def __call__(self, *args, **kwargs):
        self.call_history.append((args, kwargs))
        if len(self.responses) > 1:
            response = self.responses.pop(0)
        else:
            response = self.responses[0]
        return response

    def args_from_last_call(self):
        args, kwargs = self.call_history[-1]
        return args

    def kwargs_from_last_call(self):
        args, kwargs = self.call_history[-1]
        return kwargs


class TestRedirection(TestCase):

    def setUp(self):
        self.context = open_dependency_context()
        requests_stub = EmptyFake(pattern_obj=requests)
        self.spies = MutableObject()
        self.responses = []
        for method in ('get', 'post', 'put', 'delete', 'head'):
            fake = FakeRequestsMethod(responses=self.responses)
            setattr(requests_stub, method, fake)
            setattr(self.spies, method, fake)
        self.context.inject(requests, requests_stub)

    def tearDown(self):
        self.context.close()

    def queue_response(self, status_code, location=None):
        response = requests.Response()
        response.status_code = status_code
        if location is not None:
            response.headers['Location'] = location
        self.responses.append(response)

    def test_repeats_initial_request_headers(self):
        headers = {'spams': 22, 'eggs': 7, 'the-spanish-inquisition': 'fang'}
        self.queue_response(status_code=301, location='http://ratses')
        self.queue_response(status_code=200)
        HttpClient().get('something', headers=headers)
        expect(self.spies.get.kwargs_from_last_call()).to(
            have_keys(headers=headers))

    def test_repeats_initial_request_data(self):
        data = "But it's my only line!"
        self.queue_response(status_code=301, location='http://ratses')
        self.queue_response(status_code=200)
        HttpClient().get('something', data=data)
        expect(self.spies.get.kwargs_from_last_call()).to(
            have_keys(data=data))

    def test_repeats_arbitrary_keyword_arguments(self):
        planted = {
            'slogan': 'Nobody rejects the Spinach Imposition!',
            'weapons': ['surprise', 'fear', 'ruthless efficiency']}
        self.queue_response(status_code=301, location='http://ratses')
        self.queue_response(status_code=200)
        HttpClient().get('something', **planted)
        expect(self.spies.get.kwargs_from_last_call()).to(
            have_keys(**planted))

    def check_follows_absolute_location(self, status_code):
        location = 'https://somewhere.else/spam?eggs#sausage'
        self.queue_response(status_code=status_code, location=location)
        self.queue_response(status_code=200)
        HttpClient().get('something')
        expect(self.spies.get.args_from_last_call()[0]).to(
            equal(location))

    def test_follows_absolute_location_url_for_301(self):
        self.check_follows_absolute_location(status_code=301)

    def test_follows_absolute_location_url_for_302(self):
        self.check_follows_absolute_location(status_code=302)

    def test_follows_absolute_location_url_for_303(self):
        self.check_follows_absolute_location(status_code=303)

    def test_does_not_handle_305(self):
        self.queue_response(status_code=305, location='http://some-proxy')
        self.queue_response(status_code=200)
        client = HttpClient()
        expect(lambda: client.get('http://something')).to(
            complain(HttpUseProxy))

    def test_follows_absolute_location_url_for_307(self):
        self.check_follows_absolute_location(status_code=307)

    def test_follows_absolute_location_url_for_308(self):
        self.check_follows_absolute_location(status_code=308)

    def test_complains_about_infinite_redirects(self):
        self.queue_response(
            status_code=301, location='http://strawberry-fields')
        client = HttpClient()
        expect(lambda: client.get('http://somewhere')).to(
            complain(TooManyRedirects))

    def test_complains_if_response_lacks_location_header(self):
        self.queue_response(status_code=301, location=None)
        self.queue_response(status_code=200)
        client = HttpClient()
        expect(lambda: client.get('http://it')).to(
            complain(InvalidHttpResponse))

    def test_complains_if_location_header_is_empty(self):
        self.queue_response(status_code=301, location='')
        self.queue_response(status_code=200)
        client = HttpClient()
        expect(lambda: client.get('http://it')).to(
            complain(InvalidHttpResponse))

    def test_follows_relative_location_url(self):
        original = 'https://some-host:42/some/resource?key=val#some-fragment'
        original_parsed = urlparse(original)
        redirect = '/yadda?something=12#another-fragment'

        self.queue_response(status_code=301, location=redirect)
        self.queue_response(status_code=200)
        HttpClient().get(original)
        expect(self.spies.get.args_from_last_call()[0]).to(
            equal(url_append(
                f'{original_parsed.scheme}://{original_parsed.netloc}',
                redirect)))

    def test_preserves_fragment_if_none_specified_in_location_header(self):
        # As required by RFC 7231 section 7.1.2
        original = 'https://some-host:42/some/resource?key=val#some-fragment'
        original_parsed = urlparse(original)
        redirect = '/yadda?something=12'

        self.queue_response(status_code=301, location=redirect)
        self.queue_response(status_code=200)
        HttpClient().get(original)
        expect(self.spies.get.args_from_last_call()[0]).to(
            equal(url_append(
                f'{original_parsed.scheme}://{original_parsed.netloc}',
                redirect) + f'#{original_parsed.fragment}'))


if '__main__' == __name__:
    main()
