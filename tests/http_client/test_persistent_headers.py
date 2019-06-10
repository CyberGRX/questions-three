from unittest import TestCase, main

from expects import expect, contain
import requests
from twin_sister import open_dependency_context

from questions_three.http_client import HttpClient
from twin_sister.expects_matchers import contain_all_items_in, \
    contain_key_with_value
from twin_sister.fakes import EmptyFake, MasterSpy


class FakeResponse(EmptyFake):

    def __init__(self):
        self.status_code = 200

    def __getattr__(self,  name):
        return self


class FakeRequests():

    def __init__(self):
        self.call_history = []
        self.session_spy = MasterSpy(FakeResponse())

    def Session(self):
        return self.session_spy

    def __call__(self, *args, **kwargs):
        self.call_history.append((args, kwargs))
        return FakeResponse()

    def __getattr__(self, name):
        return self


class TestPersistentHeaders(TestCase):

    def setUp(self):
        self.context = open_dependency_context()
        self.spy = FakeRequests()
        self.context.inject(requests, self.spy)

    def tearDown(self):
        self.context.close()

    def extract_request_headers(self):
        args, kwargs = self.spy.call_history[-1]
        if 'headers' in kwargs.keys():
            return kwargs['headers']
        return {}

    def test_header_appears_in_next_request(self):
        key = 'x-spam'
        value = 'eggs'
        sut = HttpClient()
        sut.set_persistent_headers(**{key: value})
        sut.get('http://spam')
        expect(self.extract_request_headers()).to(
            contain_key_with_value(key, value))

    def test_header_appears_in_subsequent_request(self):
        key = 'x-spam'
        value = 'eggs'
        sut = HttpClient()
        sut.set_persistent_headers(**{key: value})
        sut.get('http://spam')
        sut.get('http://eggs')
        expect(self.extract_request_headers()).to(
            contain_key_with_value(key, value))

    def test_can_add_second_persistent_header(self):
        key = 'x-spam'
        value = 'eggs'
        sut = HttpClient()
        sut.set_persistent_headers(something='13')
        sut.set_persistent_headers(**{key: value})
        sut.get('http://spam')
        expect(self.extract_request_headers()).to(
            contain_key_with_value(key, value))

    def test_first_header_persists_after_adding_second(self):
        key = 'x-spam'
        value = 'eggs'
        sut = HttpClient()
        sut.set_persistent_headers(**{key: value})
        sut.set_persistent_headers(something='13')
        sut.get('http://spam')
        expect(self.extract_request_headers()).to(
            contain_key_with_value(key, value))

    def test_can_set_multiple_headers_in_one_call(self):
        headers = {'spam': 'eggs', 'sausage': 'beans', 'x': 'y'}
        sut = HttpClient()
        sut.set_persistent_headers(**headers)
        sut.get('http://parrot')
        expect(self.extract_request_headers()).to(
            contain_all_items_in(headers))

    def test_also_sends_specified_headers(self):
        headers = {'spam': 'eggs', 'sausage': 'beans', 'x': 'y'}
        sut = HttpClient()
        sut.set_persistent_headers(cardinal='ximinez', ordinal='biggles')
        sut.get('http://larch', headers=headers)
        expect(self.extract_request_headers()).to(
            contain_all_items_in(headers))

    def test_specified_header_overrides_persistent(self):
        key = 'page'
        value = 'LIX'
        sut = HttpClient()
        sut.set_persistent_headers(**{key: 'something-else'})
        sut.get('http://yadda', headers={key: value})
        expect(self.extract_request_headers()).to(
            contain_key_with_value(key, value))

    def test_can_change_a_persistent_header(self):
        key = 'thing'
        value = 'new-value'
        sut = HttpClient()
        sut.set_persistent_headers(**{key: 'old-value'})
        sut.set_persistent_headers(**{key: value})
        sut.get('http://things')
        expect(self.extract_request_headers()).to(
            contain_key_with_value(key, value))

    def test_setting_header_to_none_removes_it(self):
        key = 'something'
        sut = HttpClient()
        sut.set_persistent_headers(**{key: 'spam'})
        sut.set_persistent_headers(**{key: None})
        sut.get('http://albatross')
        expect(self.extract_request_headers().keys()).not_to(
            contain(key))

    def test_setting_non_existent_header_to_none_has_no_effect(self):
        key = 'yadda'
        sut = HttpClient()
        sut.set_persistent_headers(**{key: None})
        sut.get('http://albatross')
        expect(self.extract_request_headers().keys()).not_to(
            contain(key))

    def test_enabling_cookies_does_not_break_this_feature(self):
        key = 'spam'
        value = 'eggs'
        sut = HttpClient()
        sut.enable_cookies()
        sut.set_persistent_headers(**{key: value})
        sut.get('http://something')
        spy = self.spy.session_spy.attribute_spies['prepare_request']
        args, kwargs = spy.call_history[-1]
        request = args[0]
        expect(request.headers).to(contain_key_with_value(key, value))


if '__main__' == __name__:
    main()
