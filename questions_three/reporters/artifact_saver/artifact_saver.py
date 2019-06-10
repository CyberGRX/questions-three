import mimetypes
import os
from string import digits, ascii_letters

from twin_sister import dependency

from questions_three.event_broker.handler_detection \
    import subscribe_event_handlers
from questions_three.module_cfg import config_for_module
from questions_three.vanilla import random_base36_string


def extension_for_type(mime_type):
    """
    mimetypes.guess_extension introduces some bizarre randomness.
    This function removes it for the extensions that interest us most.
    """
    ext = None
    if 'image/png' == mime_type:
        ext = '.png'
    elif 'text/plain' == mime_type:
        ext = '.txt'
    elif 'text/html' == mime_type:
        ext = '.html'
    elif 'application/json' == mime_type:
        ext = '.json'
    elif mime_type:
        ext = mimetypes.guess_extension(mime_type)
    return ext or '.bin'


def sanitize_filename(ugly):
    return ''.join(map(
        lambda c: c if c in ascii_letters + digits + '.-_' else '_',
        ugly))


class ArtifactSaver:

    def __init__(self):
        self._suite_name = 'suiteless'

    def activate(self):
        subscribe_event_handlers(self)

    def reports_path(self):
        config = config_for_module(__name__)
        return config.reports_path

    def save(self, *, artifact, path, filename, mode):
        full_path = os.path.join(self.reports_path(), path)
        dependency(os).makedirs(full_path, exist_ok=True)
        with dependency(open)(
                os.path.join(full_path, filename), mode) as f:
            f.write(artifact)

    def path_for_artifact(self, suite_name, test_name):
        if suite_name is None:
            suite_name = self._suite_name if test_name else ''
        if test_name is None:
            test_name = ''
        return os.path.join(
            'artifacts',
            sanitize_filename(suite_name),
            sanitize_filename(test_name))

    @staticmethod
    def filename_for_artifact(
            *, artifact_group, artifact_type, mime_type):
        if artifact_type is None:
            artifact_type = ''
        return '%s%s-%s%s' % (
            artifact_group + '-' if artifact_group else '',
            artifact_type or 'artifact',
            random_base36_string(length=6),  # collision: 1 in 2.2 billion
            extension_for_type(mime_type))

    def on_artifact_created(
            self, artifact, artifact_group=None, artifact_type=None,
            artifact_mime_type=None, suite_name=None,
            test_name=None, **kwargs):
        path = self.path_for_artifact(suite_name, test_name)
        filename = self.filename_for_artifact(
            artifact_group=artifact_group,
            artifact_type=artifact_type,
            mime_type=artifact_mime_type)
        mode = 'wb' if 'decode' in dir(artifact) else 'w'
        self.save(artifact=artifact, path=path, filename=filename, mode=mode)

    def on_report_created(self, report_filename, report_content, **kwargs):
        self.save(
            artifact=report_content,
            path='',
            filename=sanitize_filename(report_filename),
            mode='w')

    def on_suite_started(self, suite_name, **kwargs):
        self._suite_name = suite_name
