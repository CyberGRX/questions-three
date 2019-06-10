from unittest import TestCase, main

from expects import expect, equal
from twin_sister import open_dependency_context

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker, subscribe_event_handlers
from questions_three.exceptions import TestSkipped
from questions_three.scaffolds \
    import disable_default_reporters, enable_default_reporters
from questions_three.scaffolds.xunit import TestSuite


suite_ended = TestEvent.suite_ended
suite_erred = TestEvent.suite_erred
suite_started = TestEvent.suite_started
test_ended = TestEvent.test_ended
test_erred = TestEvent.test_erred
test_failed = TestEvent.test_failed
test_skipped = TestEvent.test_skipped
test_started = TestEvent.test_started


class TestEventOrder(TestCase):

    def setUp(self):
        self.context = open_dependency_context(supply_logging=True)
        EventBroker.reset()
        disable_default_reporters()
        subscribe_event_handlers(self)
        self.event_order = []

    def tearDown(self):
        EventBroker.reset()
        enable_default_reporters()
        self.context.close()

    def on_suite_ended(self, **kwargs):
        self.event_order.append(suite_ended)

    def on_suite_erred(self, **kwargs):
        self.event_order.append(suite_erred)

    def on_suite_started(self, **kwargs):
        self.event_order.append(suite_started)

    def on_test_ended(self, **kwargs):
        self.event_order.append(test_ended)

    def on_test_erred(self, **kwargs):
        self.event_order.append(test_erred)

    def on_test_failed(self, **kwargs):
        self.event_order.append(test_failed)

    def on_test_skipped(self, **kwargs):
        self.event_order.append(test_skipped)

    def on_test_started(self, **kwargs):
        self.event_order.append(test_started)

    def test_happy_path(self):
        def run_suite():

            class Suite(TestSuite):
                def test_nothing(self):
                    pass
        run_suite()
        expect(self.event_order).to(equal(
            [suite_started, test_started, test_ended, suite_ended]))

    def test_suite_setup_error(self):
        def run_suite():

            class Suite(TestSuite):

                def setup_suite(self):
                    raise RuntimeError('intentional')

                def test_nothing(self):
                    pass
        run_suite()
        expect(self.event_order).to(equal(
            [suite_started, suite_erred, test_skipped, suite_ended]))

    def test_test_setup_error(self):
        def run_suite():

            class Suite(TestSuite):

                def setup(self):
                    raise RuntimeError('intentional')

                def test_should_not_run(self):
                    pass
        run_suite()
        expect(self.event_order).to(equal(
            [
                suite_started, test_started, test_erred, test_ended,
                suite_ended]))

    def test_test_error(self):
        def run_suite():

            class Suite(TestSuite):

                def test_go_boom(self):
                    raise RuntimeError('intentional')
        run_suite()
        expect(self.event_order).to(equal([
            suite_started, test_started, test_erred, test_ended,
            suite_ended]))

    def test_test_failure(self):
        def run_suite():

            class Suite(TestSuite):

                def test_fails(self):
                    raise AssertionError('intentional')
        run_suite()
        expect(self.event_order).to(equal([
            suite_started, test_started, test_failed, test_ended,
            suite_ended]))

    def test_test_skip(self):
        def run_suite():

            class Suite(TestSuite):

                def test_fails(self):
                    raise TestSkipped('intentional')
        run_suite()
        expect(self.event_order).to(equal([
            suite_started, test_started, test_skipped, test_ended,
            suite_ended]))

    def test_test_teardown_failure(self):
        def run_suite():

            class Suite(TestSuite):

                def test_nothing(self):
                    pass

                def teardown(self):
                    raise RuntimeError('intentional')

        run_suite()
        expect(self.event_order).to(equal([
            suite_started, test_started, test_erred, test_ended, suite_ended]))

    def test_suite_teardown_failure(self):
        def run_suite():

            class Suite(TestSuite):
                def test_nothing(self):
                    pass

                def teardown_suite(self):
                    raise RuntimeError('intentional')

        run_suite()
        expect(self.event_order).to(equal([
            suite_started, test_started, test_ended,
            suite_erred, suite_ended]))


if '__main__' == __name__:
    main()
