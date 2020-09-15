from unittest import TestCase, main

from expects import expect, equal
from twin_sister import open_dependency_context

from questions_three.event_broker import EventBroker
from questions_three.reporters.artifact_saver import ArtifactSaver
from questions_three.reporters.event_logger import EventLogger
from questions_three.reporters.junit_reporter import JunitReporter
from questions_three.reporters.result_compiler import ResultCompiler
from questions_three.scaffolds.common.activate_reporters import activate_reporters


def extract_active_reporters():
    return set([s.__self__.__class__ for s in EventBroker.get_subscribers()])


class TestConfiguredReporters(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_logging=True)
        EventBroker.reset()

    def tearDown(self):
        self.context.close()

    def test_module_defaults(self):
        activate_reporters()
        expect(extract_active_reporters()).to(equal({ArtifactSaver, EventLogger, JunitReporter, ResultCompiler}))

    def test_can_specify_subset_of_defaults(self):
        self.context.set_env(EVENT_REPORTERS="EventLogger,ResultCompiler")
        activate_reporters()
        expect(extract_active_reporters()).to(equal({EventLogger, ResultCompiler}))


if "__main__" == __name__:
    main()
