from contextlib import contextmanager
from string import ascii_letters, digits
import os
from unittest import TestCase, main

from expects import expect, contain, end_with, equal, start_with
from twin_sister import open_dependency_context

from questions_three.constants import TestEvent
from twin_sister.expects_matchers import contain_key_with_value
from questions_three.event_broker import EventBroker
from questions_three.reporters.artifact_saver import ArtifactSaver
from twin_sister.fakes import MasterSpy


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


def publish(artifact='spam', **kwargs):
    EventBroker.publish(
        event=TestEvent.artifact_created, artifact=artifact, **kwargs)


class TestArtifactSaving(TestCase):

    def setUp(self):
        EventBroker.reset()
        self.context = open_dependency_context(supply_env=True, supply_fs=True)
        self.fake_file = FakeFile()
        self.context.inject(open, self.fake_file.open)
        self.makedirs_spy = MasterSpy(self.context.os.makedirs)
        self.context.os.makedirs = self.makedirs_spy
        reports_path = '/where/oh/where'
        self.artifacts_path = os.path.join(reports_path, 'artifacts')
        self.context.os.environ['reports_path'] = reports_path
        self.sut = ArtifactSaver()
        self.sut.activate()

    def tearDown(self):
        self.context.close()

    def test_creates_required_directories(self):
        suite_name = 'TheBestSuite'
        test_name = 'SomethingROtter'
        publish(suite_name=suite_name, test_name=test_name)
        args, kwargs = self.makedirs_spy.call_history[0]
        expect(args[0]).to(equal(os.path.join(
            self.artifacts_path, suite_name, test_name)))

    def test_creates_directories_with_exist_ok(self):
        publish()
        args, kwargs = self.makedirs_spy.call_history[0]
        expect(kwargs).to(contain_key_with_value('exist_ok', True))

    def test_saves_artifact_without_suite_to_artifacts_directory(self):
        publish()
        actual_path, _ = os.path.split(self.fake_file.filename)
        expect(actual_path).to(equal(self.artifacts_path))

    def test_saves_artifact_with_suite_only_to_suite_directory(self):
        suite_name = 'SpammySuite'
        publish(suite_name=suite_name)
        actual_path, _ = os.path.split(self.fake_file.filename)
        expect(actual_path).to(
            equal(os.path.join(self.artifacts_path, suite_name)))

    def test_saves_artifact_with_suite_and_test_to_test_dir_under_suite(self):
        suite_name = 'Libations'
        test_name = 'test_tea'
        EventBroker.publish(
            event=TestEvent.suite_started, suite_name=suite_name)
        publish(test_name=test_name)
        actual_path, _ = os.path.split(self.fake_file.filename)
        expect(actual_path).to(equal(os.path.join(
                self.artifacts_path, suite_name, test_name)))

    def test_saves_artifact_with_test_only_to_test_dir_under_unknown(self):
        test_name = 'lost-test'
        publish(test_name=test_name)
        actual_path, _ = os.path.split(self.fake_file.filename)
        expect(actual_path).to(equal(os.path.join(
                self.artifacts_path, 'suiteless', test_name)))

    def test_removes_unsafe_chars_from_test_name(self):
        ugly = 'I\' f!@#$0-_%\\^&*/()?><",;:`blah+\t\n=.pas'
        pretty = ''.join(map(
            lambda c: c if c in ascii_letters + digits + '-_.' else '_',
            ugly))
        publish(test_name=ugly)
        expect(self.fake_file.filename).to(contain(pretty))

    def test_opens_file_for_writing_binary(self):
        publish(artifact=b'I am bytes')
        expect(self.fake_file.mode).to(equal('wb'))

    def test_opens_file_as_text_if_artifact_not_binary(self):
        publish(artifact='I am a string')
        expect(self.fake_file.mode).to(equal('w'))

    def test_writes_artifact_bytes(self):
        expected = b'bbbbbbbbbob'
        publish(artifact=expected)
        expect(self.fake_file.written).to(equal(expected))

    def test_names_file_with_artifact_type_if_provided(self):
        expected = 'holy-grail'
        publish(artifact_type=expected)
        path, filename = os.path.split(self.fake_file.filename)
        expect(filename).to(contain(expected))

    def test_names_file_with_artifact_if_type_not_provided(self):
        publish()
        path, filename = os.path.split(self.fake_file.filename)
        expect(filename).to(contain('artifact'))

    def test_names_file_with_random_characters_for_uniqueness(self):
        publish()
        path, name1 = os.path.split(self.fake_file.filename)
        publish()
        path, name2 = os.path.split(self.fake_file.filename)
        expect(name2).not_to(equal(name1))

    def test_filename_starts_with_artifact_group(self):
        group = '782a'
        kind = 'raspberry'
        publish(artifact_group=group, artifact_type=kind)
        path, name = os.path.split(self.fake_file.filename)
        expect(name).to(start_with('%s-%s' % (group, kind)))

    def test_uses_png_extension_for_png_type(self):
        publish(artifact_mime_type='image/png')
        expect(self.fake_file.filename).to(end_with('.png'))

    def test_uses_txt_extension_for_text_type(self):
        publish(artifact_mime_type='text/plain')
        expect(self.fake_file.filename).to(end_with('.txt'))

    def test_uses_html_extension_for_html_type(self):
        publish(artifact_mime_type='text/html')
        expect(self.fake_file.filename).to(end_with('.html'))

    def test_uses_json_extension_for_json_type(self):
        publish(artifact_mime_type='application/json')
        expect(self.fake_file.filename).to(end_with('.json'))

    def test_uses_bin_extension_for_unknown_type(self):
        publish(artifact_mime_type='mystery/spam')
        expect(self.fake_file.filename).to(end_with('.bin'))


if '__main__' == __name__:
    main()
