from string import ascii_letters, digits
from unittest import TestCase, main

import boto3
from expects import expect, contain, end_with, equal, have_length, start_with
from twin_sister import open_dependency_context

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three_aws.s3_artifact_saver import S3ArtifactSaver
from twin_sister.fakes import EndlessFake, FunctionSpy


def publish_artifact(artifact='spam', **kwargs):
    EventBroker.publish(
        event=TestEvent.artifact_created, artifact=artifact, **kwargs)


def publish_report(filename='spam', content='spam'):
    EventBroker.publish(
        event=TestEvent.report_created,
        report_filename=filename, report_content=content)


class BotoStub(EndlessFake):

    def __init__(self):
        super().__init__()
        self.s3_put_object_spy = FunctionSpy()

    def client(self, service_name):
        client = EndlessFake()
        if 's3' == service_name:
            client.put_object = self.s3_put_object_spy
        return client


class TestArtifactSaving(TestCase):

    def setUp(self):
        EventBroker.reset()
        self.context = open_dependency_context(
            supply_env=True)
        EventBroker.reset()
        boto_stub = BotoStub()
        self.put_spy = boto_stub.s3_put_object_spy
        self.context.inject(boto3, boto_stub)
        self.context.set_env(S3_BUCKET_FOR_ARTIFACTS='something')
        self.sut = S3ArtifactSaver()
        self.sut.activate()

    def tearDown(self):
        self.context.close()

    def test_saves_artifact_to_configured_bucket(self):
        bucket = 'Hyacinth'
        self.context.set_env(S3_BUCKET_FOR_ARTIFACTS=bucket)
        publish_artifact()
        expect(self.put_spy['Bucket']).to(equal(bucket))

    def xest_complains_if_bucket_not_configured(self):
        self.context.unset_env('S3_BUCKET_FOR_ARTIFACTS')
        publish_artifact()
        expect(self.put_spy.kwargs).to(equal(None))
        levels = [rec.levelname for rec in self.context.logging.stored_records]
        expect(levels).to(contain('ERROR'))

    def extract_key_parts(self):
        parts = self.put_spy['Key'].split('/')
        expect(parts).to(have_length(5))
        return parts

    def xest_saves_under_run_id(self):
        planted = 'i-didnt-do-it-nobody-saw-me-do-it-you-cant-prove-anything'
        self.context.set_env(TEST_RUN_ID=planted)
        publish_artifact()
        run_id, kind, suite, test, filename = self.extract_key_parts()
        expect(run_id).to(equal(planted))

    def xest_saves_artifact_without_suite_to_suiteless_directory(self):
        publish_artifact()
        run_id, kind, suite, test, filename = self.extract_key_parts()
        expect(suite).to(equal('_no_suite_supplied'))

    def xest_saves_artifact_with_suite_only_to_testless_directory(self):
        publish_artifact(suite_name='something')
        run_id, kind, suite, test, filename = self.extract_key_parts()
        expect(test).to(equal('_no_test_supplied'))

    def xest_saves_artifact_with_suite_and_test_to_test_dir_under_suite(self):
        suite_name = 'Libations'
        test_name = 'test_tea'
        EventBroker.publish(
            event=TestEvent.suite_started, suite_name=suite_name)
        publish_artifact(test_name=test_name)
        run_id, kind, suite, test, filename = self.extract_key_parts()
        expect(suite).to(equal(suite_name))
        expect(test).to(equal(test_name))

    def xest_saves_artifact_with_test_only_to_test_dir_under_unknown(self):
        test_name = 'lost-test'
        publish_artifact(test_name=test_name)
        run_id, kind, suite, test, filename = self.extract_key_parts()
        expect(suite).to(equal('_no_suite_supplied'))

    def xest_removes_unsafe_chars_from_test_name(self):
        ugly = 'I\' f!@#$0-_%\\^&*/()?><",;:`blah+\t\n=.pas'
        pretty = ''.join(map(
            lambda c: c if c in ascii_letters + digits + '-_.' else '_',
            ugly))
        publish_artifact(test_name=ugly)
        run_id, kind, suite, test, filename = self.extract_key_parts()
        expect(test).to(equal(pretty))

    def xest_writes_artifact_bytes(self):
        expected = b'bbbbbbbbbob'
        publish_artifact(artifact=expected)
        expect(self.put_spy['Body']).to(equal(expected))

    def xest_names_file_with_artifact_type_if_provided(self):
        expected = 'holy-grail'
        publish_artifact(artifact_type=expected)
        run_id, kind, suite, test, filename = self.extract_key_parts()
        expect(filename).to(contain(expected))

    def xest_names_file_with_artifact_if_type_not_provided(self):
        publish_artifact()
        run_id, kind, suite, test, filename = self.extract_key_parts()
        expect(filename).to(contain('artifact'))

    def xest_names_file_with_random_characters_for_uniqueness(self):
        publish_artifact()
        run_id, kind, suite, test, name1 = self.extract_key_parts()
        publish_artifact()
        run_id, kind, suite, test, name2 = self.extract_key_parts()
        expect(name2).not_to(equal(name1))

    def xest_filename_starts_with_artifact_group(self):
        group = '782a'
        kind = 'raspberry'
        publish_artifact(artifact_group=group, artifact_type=kind)
        run_id, _, suite, test, name = self.extract_key_parts()
        expect(name).to(start_with('%s-%s' % (group, kind)))

    def xest_sends_content_type_if_supplied(self):
        planted = 'nonfood/SPAM'
        publish_artifact(artifact_mime_type=planted)
        expect(self.put_spy['ContentType']).to(equal(planted))

    def xest_uses_png_extension_for_png_type(self):
        publish_artifact(artifact_mime_type='image/png')
        run_id, kind, suite, test, name = self.extract_key_parts()
        expect(name).to(end_with('.png'))

    def xest_uses_txt_extension_for_text_type(self):
        publish_artifact(artifact_mime_type='text/plain')
        run_id, kind, suite, test, name = self.extract_key_parts()
        expect(name).to(end_with('.txt'))

    def xest_uses_html_extension_for_html_type(self):
        publish_artifact(artifact_mime_type='text/html')
        run_id, kind, suite, test, name = self.extract_key_parts()
        expect(name).to(end_with('.html'))

    def xest_uses_json_extension_for_json_type(self):
        publish_artifact(artifact_mime_type='application/json')
        run_id, kind, suite, test, name = self.extract_key_parts()
        expect(name).to(end_with('.json'))

    def xest_uses_bin_extension_for_unknown_type(self):
        publish_artifact(artifact_mime_type='mystery/spam')
        run_id, kind, suite, test, name = self.extract_key_parts()
        expect(name).to(end_with('.bin'))

    def xest_puts_report_under_configured_bucket(self):
        bucket = 'Richard'
        self.context.set_env(S3_BUCKET_FOR_ARTIFACTS=bucket)
        publish_report()
        expect(self.put_spy['Bucket']).to(equal(bucket))

    def xest_puts_report_directly_under_run_id(self):
        given_id = 'a-horse-with-no-name'
        given_filename = 'FRUIT.BAT'
        self.context.set_env(TEST_RUN_ID=given_id)
        publish_report(filename=given_filename)
        expect(self.put_spy['Key']).to(equal(f'{given_id}/{given_filename}'))

    def xest_puts_report_content(self):
        given = 'Oooh!  Heavens.  And I thought you were so rugged.'
        publish_report(content=given)
        expect(self.put_spy['Body']).to(equal(given))


if '__main__' == __name__:
    main()
