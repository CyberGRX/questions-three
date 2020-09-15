from logging import StreamHandler
from unittest import TestCase, main

from expects import expect, equal
from twin_sister import open_dependency_context

from questions_three.event_broker import EventBroker, subscribe_event_handlers
from questions_three.scaffolds.xunit import TestSuite
from twin_sister.fakes import EmptyFake


def run_suite():
    class Suite(TestSuite):
        def setup_suite(self):
            raise RuntimeError("I got the boogie fever")

        def test_one(self):
            pass

        def test_two(self):
            pass

        def test_three(self):
            pass


class TestSuiteSetupFailure(TestCase):
    """
    As a test developer,
    I would like the suite to automatically skip every test if setup fails
    So I do not need to skip each test individually
    """

    def setUp(self):
        self.context = open_dependency_context(supply_fs=True, supply_logging=True)
        self.context.inject(StreamHandler, EmptyFake())
        EventBroker.reset()
        subscribe_event_handlers(self)
        self.skip_events = 0

    def tearDown(self):
        self.context.close()

    def on_test_skipped(self, **kwargs):
        self.skip_events += 1

    def test_skips_all_tests(self):
        run_suite()
        expect(self.skip_events).to(equal(3))  # number of tests


if "__main__" == __name__:
    main()
