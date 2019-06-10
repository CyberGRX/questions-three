from contextlib import contextmanager
from datetime import datetime
from unittest import TestCase, main

from expects import expect, equal
from twin_sister import open_dependency_context

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.reporters.result_compiler import ResultCompiler
from twin_sister.fakes import FakeDatetime


def start_suite():
    EventBroker.publish(
        event=TestEvent.suite_started, suite_name='spam')


def end_suite():
    EventBroker.publish(
        event=TestEvent.suite_ended, suite_name='spam')


@contextmanager
def test_suite():
    start_suite()
    yield
    end_suite()


def start_test():
    EventBroker.publish(
        event=TestEvent.test_started, test_name='spam')


def end_test():
    EventBroker.publish(
        event=TestEvent.test_ended, test_name='spam')


class TestTimestamps(TestCase):

    def setUp(self):
        self.context = open_dependency_context()
        self.fake_time = FakeDatetime()
        self.context.inject(datetime, self.fake_time)
        self.results = None
        EventBroker.subscribe(
            event=TestEvent.suite_results_compiled,
            func=self.capture_results)
        self.sut = ResultCompiler()
        self.sut.activate()

    def tearDown(self):
        self.context.close()

    def capture_results(self, suite_results, **kwargs):
        self.results = suite_results

    def test_records_test_start_time(self):
        unexpected = datetime.fromtimestamp(0)
        expected = datetime.fromtimestamp(1516896985.203114)
        self.fake_time.fixed_time = unexpected
        with test_suite():
            self.fake_time.fixed_time = expected
            start_test()
            self.fake_time.fixed_time = unexpected
            end_test()
        expect(self.results.tests[0].start_time).to(equal(expected))

    def test_records_test_end_time(self):
        unexpected = datetime.fromtimestamp(0)
        expected = datetime.fromtimestamp(1516896985.203114)
        self.fake_time.fixed_time = unexpected
        with test_suite():
            start_test()
            self.fake_time.fixed_time = expected
            end_test()
            self.fake_time.fixed_time = unexpected
        expect(self.results.tests[0].end_time).to(equal(expected))

    def test_records_suite_start_time(self):
        unexpected = datetime.fromtimestamp(0)
        expected = datetime.fromtimestamp(1516896985.203114)
        self.fake_time.fixed_time = expected
        start_suite()
        self.fake_time.fixed_time = unexpected
        end_suite()
        expect(self.results.suite_start_time).to(equal(expected))

    def test_records_suite_end_time(self):
        unexpected = datetime.fromtimestamp(0)
        expected = datetime.fromtimestamp(1516896985.203114)
        self.fake_time.fixed_time = unexpected
        start_suite()
        self.fake_time.fixed_time = expected
        end_suite()
        expect(self.results.suite_end_time).to(equal(expected))


if '__main__' == __name__:
    main()
