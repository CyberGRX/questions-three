from logging import StreamHandler
from unittest import TestCase, main

from expects import expect, contain, equal
from twin_sister import open_dependency_context

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker, subscribe_event_handlers
from questions_three.exceptions import TestSkipped
from questions_three.scaffolds.xunit import TestSuite
from twin_sister.fakes import EmptyFake


class TestSkipAllTests(TestCase):
    """
    As a test developer,
    I would like to mark an entire suite as skipped
    So I can skip suites in a systematic way and avoid side effects
      from needless suite setup
    """

    def run_suite(self):
        class SkippedSuite(TestSuite):
            def setup_suite(suite):
                raise TestSkipped(self.skip_msg)

            def teardown_suite(suite):
                self.suite_teardown_ran = True

            def setup(suite):
                self.test_setup_ran = True

            def teardown(suite):
                self.test_teardown_ran = True

            def test_one(suite):
                pass

            def test_two(suite):
                pass

            def test_three(suite):
                pass

    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_fs=True, supply_logging=True)
        self.context.inject(StreamHandler, EmptyFake())
        EventBroker.reset()
        subscribe_event_handlers(self)
        self.skip_events = 0
        self.skip_msg = "intentional"
        self.suite_teardown_ran = False
        self.test_setup_ran = False
        self.test_teardown_ran = False

    def tearDown(self):
        self.context.close()

    def on_test_skipped(self, **kwargs):
        self.skip_events += 1

    def test_skips_all_tests(self):
        self.run_suite()
        expect(self.skip_events).to(equal(3))  # number of tests

    def test_does_not_run_test_setup(self):
        self.run_suite()
        assert not self.test_setup_ran, "Setup ran"

    def test_does_not_run_test_teardown(self):
        self.run_suite()
        assert not self.test_teardown_ran, "Teardown ran"

    def test_does_not_run_suite_teardown(self):
        self.run_suite()
        assert not self.suite_teardown_ran, "Teardown ran"

    def test_repeats_skip_message_for_tests(self):
        caught = None

        def on_test_skipped(*, exception, **kwargs):
            nonlocal caught
            caught = exception

        EventBroker.subscribe(event=TestEvent.test_skipped, func=on_test_skipped)

        self.skip_msg = "Sometimes you feel like a nut.  Sometimes you don't."
        self.run_suite()
        expect(str(caught)).to(contain(self.skip_msg))


if "__main__" == __name__:
    main()
