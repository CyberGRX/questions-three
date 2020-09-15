from unittest import TestCase, main

from expects import expect, equal, have_length
from questions_three.exceptions import TestSkipped
from questions_three.vanilla import format_exception
from twin_sister import open_dependency_context

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.logging import logger_for_module
from questions_three.reporters.event_logger import EventLogger


class LogSpy:
    def __init__(self):
        self.entries = []

    def _logging_func(self, level):
        def func(msg):
            self.entries.append((level, msg))

        return func

    def __getattr__(self, name):
        return self._logging_func(level=name)


class TestLogging(TestCase):
    def setUp(self):
        self.context = open_dependency_context()
        self.log_spy = LogSpy()
        self.context.inject(logger_for_module, lambda *a, **k: self.log_spy)
        self.sut = EventLogger()
        self.sut.activate()

    def tearDown(self):
        self.context.close()
        EventBroker.reset()

    def logged(self):
        expect(self.log_spy.entries).to(have_length(1))
        return self.log_spy.entries[0]

    def test_suite_ended_level(self):
        EventBroker.publish(event=TestEvent.suite_ended, suite_name="spam")
        level, msg = self.logged()
        expect(level).to(equal("info"))

    def test_suite_ended_message(self):
        suite_name = "SomethingSuite"
        EventBroker.publish(event=TestEvent.suite_ended, suite_name=suite_name)
        level, msg = self.logged()
        expect(msg).to(equal('Suite "%s" ended' % suite_name))

    def test_suite_erred_level(self):
        EventBroker.publish(event=TestEvent.suite_erred, exception=RuntimeError(), suite_name="spam")
        level, msg = self.logged()
        expect(level).to(equal("error"))

    def test_suite_erred_message(self):
        err = RuntimeError("something broke")
        EventBroker.publish(event=TestEvent.suite_erred, suite_name="spam", exception=err)
        level, msg = self.logged()
        expect(msg).to(equal(format_exception(err)))

    def test_suite_started_level(self):
        EventBroker.publish(event=TestEvent.suite_started, suite_name="spam")
        level, msg = self.logged()
        expect(level).to(equal("info"))

    def test_suite_started_message(self):
        suite_name = "SomethingSuite"
        EventBroker.publish(event=TestEvent.suite_started, suite_name=suite_name)
        level, msg = self.logged()
        expect(msg).to(equal('Suite "%s" started' % suite_name))

    def test_test_ended_level(self):
        EventBroker.publish(event=TestEvent.test_ended, test_name="spam")
        level, msg = self.logged()
        expect(level).to(equal("info"))

    def test_test_ended_message(self):
        test_name = "Get on with it!"
        EventBroker.publish(event=TestEvent.test_ended, test_name=test_name)
        level, msg = self.logged()
        expect(msg).to(equal('Check "%s" ended' % test_name))

    def test_test_erred_level(self):
        EventBroker.publish(event=TestEvent.test_erred, exception=RuntimeError(), test_name="spam")
        level, msg = self.logged()
        expect(level).to(equal("error"))

    def test_test_erred_message(self):
        err = RuntimeError("So. There.")
        EventBroker.publish(event=TestEvent.test_erred, exception=err)
        level, msg = self.logged()
        expect(msg).to(equal(format_exception(err)))

    def test_test_failed_level(self):
        EventBroker.publish(event=TestEvent.test_failed, test_name="spam", exception=AssertionError())
        level, msg = self.logged()
        expect(level).to(equal("warning"))

    def test_test_failed_message(self):
        err = AssertionError("oops")
        test_name = "Test tea"
        EventBroker.publish(event=TestEvent.test_failed, exception=err, test_name=test_name)
        level, msg = self.logged()
        expect(msg).to(equal('Check "%s" failed: %s' % (test_name, err)))

    def test_test_skipped_level(self):
        err = TestSkipped("Let's not go there")
        test_name = "A rather silly place"
        EventBroker.publish(event=TestEvent.test_skipped, exception=err, test_name=test_name)
        level, msg = self.logged()
        expect(level).to(equal("warning"))

    def test_test_skipped_message(self):
        err = TestSkipped("Let's not go there")
        test_name = "A rather silly place"
        EventBroker.publish(event=TestEvent.test_skipped, exception=err, test_name=test_name)
        level, msg = self.logged()
        expect(msg).to(equal('Check "%s" skipped: %s' % (test_name, err)))

    def test_test_started_level(self):
        EventBroker.publish(event=TestEvent.test_started, test_name="spam")
        level, msg = self.logged()
        expect(level).to(equal("info"))

    def test_test_started_message(self):
        test_name = "Oh yeah?  Well, test this!"
        EventBroker.publish(event=TestEvent.test_started, test_name=test_name)
        level, msg = self.logged()
        expect(msg).to(equal('Check "%s" started' % test_name))

    def test_sample_measured_level(self):
        EventBroker.publish(
            event=TestEvent.sample_measured, test_name="spam", sample_parameters="spam", sample_execution_seconds=0
        )
        level, msg = self.logged()
        expect(level).to(equal("info"))

    def test_sample_measured_message(self):
        name = "Turkey"
        params = "argle bargle"
        seconds = 105.3
        EventBroker.publish(
            event=TestEvent.sample_measured, test_name=name, sample_parameters=params, sample_execution_seconds=seconds
        )
        level, msg = self.logged()
        expect(msg).to(equal(f"{name} completed in {seconds} seconds"))


if "__main__" == __name__:
    main()
