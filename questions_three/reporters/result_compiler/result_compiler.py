from datetime import datetime

from questions_three.constants import TestEvent, TestStatus
from questions_three.event_broker import EventBroker, \
    subscribe_event_handlers

from twin_sister import dependency

from .suite_results import SuiteResults, TestResult


def current_time():
    return dependency(datetime).now()


class ResultCompiler:

    def __init__(self):
        self.results = SuiteResults()

    def _find_or_create_test(self, test_name):
        for candidate in self.results.tests:
            if candidate.name == test_name:
                return candidate
        test = TestResult(test_name=test_name)
        test.start_time = current_time()
        test.status = TestStatus.running
        self.results.tests.append(test)
        return test

    def activate(self):
        subscribe_event_handlers(self)

    def on_artifact_created(self, artifact, test_name=None, **kwargs):
        if test_name:
            self._find_or_create_test(test_name).artifacts.append(artifact)
        else:
            self.results.artifacts.append(artifact)

    def on_suite_started(self, suite_name, **kwargs):
        self.results.suite_start_time = current_time()
        self.results.suite_name = suite_name

    def on_suite_ended(self, **kwargs):
        self.results.suite_end_time = current_time()
        EventBroker.publish(
            event=TestEvent.suite_results_compiled,
            suite_results=self.results)

    def on_suite_erred(self, exception=None, **kwargs):
        self.results.suite_exception = exception or Exception(
            'Suite erred.  No exception was provided.')

    def on_test_ended(self, test_name, **kwargs):
        test = self._find_or_create_test(test_name)
        test.end_time = current_time()
        if TestStatus.running == test.status:
            test.status = TestStatus.passed

    def on_test_erred(self, test_name, exception=None, **kwargs):
        test = self._find_or_create_test(test_name)
        test.status = TestStatus.erred
        test.exception = exception

    def on_test_failed(self, test_name, exception=None, **kwargs):
        test = self._find_or_create_test(test_name)
        test.status = TestStatus.failed
        test.exception = exception

    def on_test_skipped(self, test_name, exception=None, **kwargs):
        test = self._find_or_create_test(test_name)
        test.status = TestStatus.skipped
        test.exception = exception

    def on_test_started(self, test_name, **kwargs):
        self._find_or_create_test(test_name)
