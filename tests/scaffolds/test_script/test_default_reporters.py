import gc
import imp
from unittest import TestCase, main

from twin_sister import close_all_dependency_contexts

from questions_three.event_broker import EventBroker
from questions_three.reporters.artifact_saver import ArtifactSaver
from questions_three.reporters.event_logger import EventLogger
from questions_three.reporters.junit_reporter import JunitReporter
from questions_three.reporters.result_compiler import ResultCompiler
from questions_three.scaffolds import enable_default_reporters
import questions_three.scaffolds.test_script


def is_active(reporter_class):
    gc.collect()
    for candidate in EventBroker.get_subscribers():
        if hasattr(candidate, '__self__') and \
                isinstance(candidate.__self__, reporter_class):
            return True
    return False


class TestDefaultReporters(TestCase):

    def setUp(self):
        close_all_dependency_contexts()
        EventBroker.reset()
        enable_default_reporters()
        # The import below should cause the default reporters to be activated
        imp.reload(questions_three.scaffolds.test_script)

    def test_artifact_saver(self):
        assert is_active(ArtifactSaver), 'ArtifactSaver is not active'

    def test_result_compiler(self):
        assert is_active(ResultCompiler), 'ResultCompiler is not active'

    def test_junit_reporter(self):
        assert is_active(JunitReporter), 'JunitReporter is not active'

    def test_event_logger(self):
        assert is_active(EventLogger), \
            'EventLogger is not active'


if '__main__' == __name__:
    main()
