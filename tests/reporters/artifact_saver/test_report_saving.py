from contextlib import contextmanager
import os
from unittest import TestCase, main

from expects import expect, equal, have_length
from twin_sister import open_dependency_context

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from twin_sister.expects_matchers import contain_key_with_value
from questions_three.reporters.artifact_saver import ArtifactSaver
from twin_sister.fakes import MasterSpy


def publish(content='spam', filename='spam'):
    EventBroker.publish(
            event=TestEvent.report_created,
            report_content=content, report_filename=filename)


class FakeFile:

    def __init__(self):
        self.filename = None
        self.mode = None
        self.written = None

    def write(self, content):
        self.written = content

    @contextmanager
    def open(self, filename, mode=None, *args):
        self.filename = filename
        self.mode = mode
        yield self


class TestReportSaving(TestCase):

    def setUp(self):
        EventBroker.reset()
        self.context = open_dependency_context(supply_env=True, supply_fs=True)
        self.fake_file = FakeFile()
        self.context.inject(open, self.fake_file.open)
        self.makedirs_spy = MasterSpy(self.context.os.makedirs)
        self.context.os.makedirs = self.makedirs_spy
        self.sut = ArtifactSaver()
        self.sut.activate()

    def tearDown(self):
        self.context.close()

    def set_reports_path(self, path):
        self.context.os.environ['reports_path'] = path

    def test_saves_report_contents(self):
        content = "I'm glad I'm not an Oscar Meyer Weiner"
        publish(content=content)
        expect(self.fake_file.written).to(equal(content))

    def test_saves_report_to_configured_reports_directory(self):
        expected = '/spam/eggs/sausage/spam'
        self.set_reports_path(expected)
        publish()
        actual, _ = os.path.split(self.fake_file.filename)
        expect(actual).to(equal(expected))

    def extract_makedirs_call(self):
        calls = self.makedirs_spy.call_history
        expect(calls).to(have_length(1))
        return calls[0]

    def test_creates_full_path_to_reports_directory(self):
        expected = '/biggles/all/the/way/down/'
        self.set_reports_path(expected)
        publish()
        args, kwargs = self.extract_makedirs_call()
        expect(args[0]).to(equal(expected))

    def test_creates_path_with_exist_ok(self):
        publish()
        args, kwargs = self.extract_makedirs_call()
        expect(kwargs).to(contain_key_with_value('exist_ok', True))

    def test_creates_file_with_specified_name(self):
        expected = 'susan.ann'
        publish(filename=expected)
        _, actual = os.path.split(self.fake_file.filename)
        expect(actual).to(equal(expected))

    def test_opens_report_file_in_write_mode(self):
        publish()
        expect(self.fake_file.mode).to(equal('w'))


if '__main__' == __name__:
    main()
