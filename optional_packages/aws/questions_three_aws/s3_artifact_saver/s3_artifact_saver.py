import boto3
from twin_sister import dependency

from questions_three.exceptions import InvalidConfiguration
from questions_three.logging import logger_for_module
from questions_three.module_cfg import config_for_module
from questions_three.reporters.artifact_saver import ArtifactSaver
from questions_three.reporters.artifact_saver.artifact_saver import \
    sanitize_filename


class S3ArtifactSaver(ArtifactSaver):

    def __init__(self):
        super().__init__()
        self._suite_name = None

    def save(self, *, artifact, path, filename, content_type):
        log = logger_for_module(__name__)
        bucket = config_for_module(__name__).s3_bucket_for_artifacts
        if not bucket:
            raise InvalidConfiguration('$S3_BUCKET_FOR_ARTIFACTS is not set')
        client = dependency(boto3).client('s3')
        kwargs = {
            'Bucket': bucket,
            'Key': f'{path}/{filename}',
            'Body': artifact}
        if content_type:
            kwargs['ContentType'] = content_type
        log.debug(f'PUT {bucket}:{path}/{filename}')
        client.put_object(**kwargs)

    def path_for_artifact(self, suite_name, test_name, run_id):
        if suite_name is None:
            suite_name = self._suite_name or '_no_suite_supplied'
        if test_name is None:
            test_name = '_no_test_supplied'
        return '%s/artifacts/%s/%s' % (
            run_id,
            sanitize_filename(suite_name),
            sanitize_filename(test_name))

    def on_artifact_created(
            self, run_id, artifact, artifact_group=None, artifact_type=None,
            artifact_mime_type=None, suite_name=None,
            test_name=None, **kwargs):
        log = logger_for_module(__name__)
        path = self.path_for_artifact(suite_name, test_name, run_id)
        filename = self.filename_for_artifact(
            artifact_group=artifact_group,
            artifact_type=artifact_type,
            mime_type=artifact_mime_type)
        log.debug(f'Saving artifact {filename}')
        self.save(
            artifact=artifact, path=path, filename=filename,
            content_type=artifact_mime_type)

    def on_report_created(
            self, report_filename, report_content, run_id, **kwargs):
        log = logger_for_module(__name__)
        log.debug(f'Saving report {report_filename}')
        self.save(
            artifact=report_content,
            path=run_id,
            filename=report_filename,
            content_type=None)
