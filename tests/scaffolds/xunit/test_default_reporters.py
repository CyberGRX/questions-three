from contextlib import contextmanager
import gc
from io import StringIO
import os
from unittest import TestCase, main

from expects import expect, contain
from twin_sister import open_dependency_context

from questions_three.event_broker import EventBroker
from questions_three.module_cfg.loader import YML_FILENAME as MODULE_CFG
from questions_three.reporters.artifact_saver import ArtifactSaver
from questions_three.reporters.junit_reporter import JunitReporter
from questions_three.reporters.result_compiler import ResultCompiler
from questions_three.scaffolds import enable_default_reporters
from questions_three.scaffolds.xunit import TestSuite


def is_active(reporter_class):
    gc.collect()
    for candidate in EventBroker.get_subscribers():
        if hasattr(candidate, '__self__') and \
                isinstance(candidate.__self__, reporter_class):
            return True
    return False


@contextmanager
def fake_open(filename, *args, **kwargs):
    path, name = os.path.split(filename)
    # Use the real module configuration files
    if name == MODULE_CFG:
        f = open(filename, *args, **kwargs)
    else:
        f = StringIO()
    yield f
    f.close()


class TestDefaultReporters(TestCase):

    def setUp(self):
        self.context = open_dependency_context(supply_logging=True)
        self.context.inject_as_class(os.makedirs, lambda *args, **kwargs: None)
        self.context.inject(open, fake_open)
        enable_default_reporters()
        EventBroker.reset()
        active_reporters_at_suite_start = []

        def run_suite():
            class Suite(TestSuite):
                def setup_suite(slf):
                    for reporter in (
                            ArtifactSaver, ResultCompiler, JunitReporter):
                        if is_active(reporter):
                            active_reporters_at_suite_start.append(reporter)
        run_suite()
        self.active = active_reporters_at_suite_start

    def tearDown(self):
        self.context.close()

    def test_artifact_saver(self):
        expect(self.active).to(contain(ArtifactSaver))

    def test_result_compiler(self):
        expect(self.active).to(contain(ResultCompiler))

    def test_junit_reporter(self):
        expect(self.active).to(contain(JunitReporter))


if '__main__' == __name__:
    main()
