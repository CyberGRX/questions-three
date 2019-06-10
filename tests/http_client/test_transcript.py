from datetime import datetime
from unittest import TestCase, main

from expects import expect, contain
import requests
from twin_sister import open_dependency_context

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from twin_sister.expects_matchers import contain_key_with_value, raise_ex
from questions_three.http_client import HttpClient
from twin_sister.fakes import EmptyFake


class FakeResponse(EmptyFake):

    def __init__(self, status_code=200):
        self.status_code = status_code
        self.headers = {}
        self.text = ''


class FakeRequests:

    def __init__(self):
        self.response = FakeResponse()

    def __call__(self, *args, **kwargs):
        return self.response

    def __getattr__(self, name):
        return self


class TestTranscript(TestCase):

    def setUp(self):
        EventBroker.reset()
        self.published = None
        self.context = open_dependency_context()
        self.fake_requests = FakeRequests()
        self.context.inject(requests, self.fake_requests)
        EventBroker.subscribe(
            event=TestEvent.artifact_created, func=self.on_artifact_created)

    def tearDown(self):
        self.context.close()

    def on_artifact_created(self, **kwargs):
        self.published = kwargs

    def test_publish_with_suite_name_on_suite_erred(self):
        sut = HttpClient()
        sut.get('http://spamoni.io')
        name = 'bubba'
        EventBroker.publish(
            event=TestEvent.suite_erred, suite_name=name,
            exception=RuntimeError())
        assert self.published, 'Nothing was published'
        expect(self.published).to(
            contain_key_with_value('suite_name', name))

    def test_publish_with_test_name_on_test_erred(self):
        sut = HttpClient()
        sut.get('http://spamoni.io')
        name = 'shem'
        EventBroker.publish(
            event=TestEvent.test_erred, test_name=name,
            exception=RuntimeError())
        assert self.published, 'Nothing was published'
        expect(self.published).to(
            contain_key_with_value('test_name', name))

    def test_publish_with_test_name_on_test_failed(self):
        sut = HttpClient()
        sut.get('http://spamoni.io')
        name = 'nombre'
        EventBroker.publish(
            event=TestEvent.test_failed, test_name=name,
            exception=RuntimeError())
        assert self.published, 'Nothing was published'
        expect(self.published).to(
            contain_key_with_value('test_name', name))

    def trigger_transcript(self):
        sut = HttpClient()
        sut.get('http://yaddayadda')
        EventBroker.publish(
            event=TestEvent.test_failed, exception=RuntimeError())

    def test_artifact_mime_type_is_text_plain(self):
        self.trigger_transcript()
        expect(self.published).to(
            contain_key_with_value('artifact_mime_type', 'text/plain'))

    def test_artifact_type_is_http_transcript(self):
        self.trigger_transcript()
        expect(self.published).to(
            contain_key_with_value('artifact_type', 'http_transcript'))

    def test_request_timestamp(self):
        t = datetime.fromtimestamp(1519328797.125686)
        self.context.inject(datetime.utcnow, lambda: t)
        self.trigger_transcript()
        expect(self.published['artifact']).to(
            contain('Request at %s' % t.isoformat()))

    def test_request_method_and_url(self):
        method = 'HEAD'
        sut = HttpClient()
        url = 'http://i.love2spam.net/spam'
        getattr(sut, method.lower())(url)
        EventBroker.publish(
            event=TestEvent.test_failed, exception=RuntimeError())
        expect(self.published['artifact']).to(
            contain('\n%s %s' % (method, url)))

    def test_request_headers(self):
        headers = {'X-yz': 'yogurt humphrey', 'Content-length': 'infinite'}
        sut = HttpClient()
        sut.get('http://something', headers=headers)
        EventBroker.publish(
            event=TestEvent.test_failed, exception=RuntimeError())
        expect(self.published['artifact']).to(
            contain('\n'.join([
                '%s: %s' % (k, v) for k, v in headers.items()])))

    def test_request_payload(self):
        payload = """
        Immanuel Kant was a real pissant
        Who was very rarely stable.
        Heidigger Heidigger was a boozy beggar
        Who could think you under the table.
        David Hume could outconsume
        Schopenhauer and Hegel
        And Wittgenstein was a beery swine
        Who was just as sloshed as Schlegel.

        There's nothing Neitche couldn't teach about the raising of the wrist.
        Socrates himself was permanently pissed."""

        sut = HttpClient()
        sut.put('http://python.net/philosophers.txt', data=payload)
        EventBroker.publish(
            event=TestEvent.test_failed, exception=RuntimeError())
        expect(self.published['artifact']).to(contain(payload))

    def test_does_not_choke_on_binary_payload(self):
        def attempt():
            HttpClient().post('http://spam', data=b'spam')

        expect(attempt).not_to(raise_ex(TypeError))

    def test_does_not_choke_on_dict_payload(self):
        def attempt():
            HttpClient().post('http://spam', data={'spam': 2})

        expect(attempt).not_to(raise_ex(TypeError))

    def test_response_timestamp(self):
        t = datetime.fromtimestamp(1519328797.125686)
        self.context.inject(datetime.utcnow, lambda: t)
        self.trigger_transcript()
        expect(self.published['artifact']).to(
            contain('Response at %s' % t.isoformat()))

    def test_response_status_code(self):
        code = 242
        self.fake_requests.response.status_code = code
        self.trigger_transcript()
        expect(self.published['artifact']).to(
            contain('\n%d\n' % code))

    def test_response_headers(self):
        headers = {'X-yz': 'Sam the spammer', 'Content-length': '2'}
        self.fake_requests.response.headers = headers
        sut = HttpClient()
        sut.get('http://something')
        EventBroker.publish(
            event=TestEvent.test_failed, exception=RuntimeError())
        expect(self.published['artifact']).to(
            contain('\n'.join([
                '%s: %s' % (k, v) for k, v in headers.items()])))

    def test_response_payload(self):
        payload = 'What a heap'
        self.fake_requests.response.text = payload
        self.trigger_transcript()
        expect(self.published['artifact']).to(
            contain(payload))


if '__main__' == __name__:
    main()
