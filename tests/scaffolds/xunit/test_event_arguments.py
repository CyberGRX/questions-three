from unittest import TestCase, main

from expects import expect
from twin_sister import open_dependency_context

from questions_three.event_broker import EventBroker, subscribe_event_handlers
from questions_three.exceptions import TestSkipped
from twin_sister.expects_matchers import contain_key_with_value
from questions_three.scaffolds import disable_default_reporters, enable_default_reporters
from questions_three.scaffolds.xunit import TestSuite


class TestEventArguments(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_logging=True)
        EventBroker.reset()
        subscribe_event_handlers(self)
        disable_default_reporters()

    def tearDown(self):
        enable_default_reporters()
        self.context.close()

    def on_suite_ended(self, **kwargs):
        self.suite_ended_kwargs = kwargs

    def on_suite_erred(self, **kwargs):
        self.suite_erred_kwargs = kwargs

    def on_suite_started(self, **kwargs):
        self.suite_started_kwargs = kwargs

    def on_test_ended(self, **kwargs):
        self.test_ended_kwargs = kwargs

    def on_test_erred(self, **kwargs):
        self.test_erred_kwargs = kwargs

    def on_test_failed(self, **kwargs):
        self.test_failed_kwargs = kwargs

    def on_test_skipped(self, **kwargs):
        self.test_skipped_kwargs = kwargs

    def on_test_started(self, **kwargs):
        self.test_started_kwargs = kwargs

    def test_suite_ended_contains_suite_name(self):
        def wrapper():
            class SpammySuite(TestSuite):
                pass

        wrapper()
        expect(self.suite_ended_kwargs).to(contain_key_with_value("suite_name", "SpammySuite"))

    def test_suite_started_contains_suite_name(self):
        def wrapper():
            class SpammySuite(TestSuite):
                pass

        wrapper()
        expect(self.suite_started_kwargs).to(contain_key_with_value("suite_name", "SpammySuite"))

    def test_test_skipped_contains_suite_name(self):
        def wrapper():
            class SpammySuite(TestSuite):
                def test_something(self):
                    raise TestSkipped("yadda")

        wrapper()
        expect(self.test_skipped_kwargs).to(contain_key_with_value("suite_name", "SpammySuite"))

    def test_test_skipped_contains_test_name(self):
        def wrapper():
            class SpammySuite(TestSuite):
                def test_yogurt(self):
                    raise TestSkipped("yadda")

        wrapper()
        expect(self.test_skipped_kwargs).to(contain_key_with_value("test_name", "test_yogurt"))

    def test_test_skipped_contains_exception(self):
        e = TestSkipped("I tried to think but nothing happened.")

        def wrapper():
            class SpammySuite(TestSuite):
                def test_yogurt(self):
                    raise e

        wrapper()
        expect(self.test_skipped_kwargs).to(contain_key_with_value("exception", e))

    def test_test_erred_contains_test_name(self):
        def wrapper():
            class SpammySuite(TestSuite):
                def test_yogurt(self):
                    raise RuntimeError("yadda")

        wrapper()
        expect(self.test_erred_kwargs).to(contain_key_with_value("test_name", "test_yogurt"))

    def test_test_erred_contains_suite_name(self):
        def wrapper():
            class SpammySuite(TestSuite):
                def test_yogurt(self):
                    raise RuntimeError("yadda")

        wrapper()
        expect(self.test_erred_kwargs).to(contain_key_with_value("suite_name", "SpammySuite"))

    def test_test_erred_contains_exception(self):
        e = RuntimeError("Nobody injests the Spinach Imposition!")

        def wrapper():
            class SpammySuite(TestSuite):
                def test_yogurt(self):
                    raise e

        wrapper()
        expect(self.test_erred_kwargs).to(contain_key_with_value("exception", e))

    def test_test_failed_contains_test_name(self):
        def wrapper():
            class SpammySuite(TestSuite):
                def test_yogurt(self):
                    assert False, "oops"

        wrapper()
        expect(self.test_failed_kwargs).to(contain_key_with_value("test_name", "test_yogurt"))

    def test_test_failed_contains_suite_name(self):
        def wrapper():
            class SpammySuite(TestSuite):
                def test_yogurt(self):
                    assert False, "oops"

        wrapper()
        expect(self.test_failed_kwargs).to(contain_key_with_value("suite_name", "SpammySuite"))

    def test_test_failed_contains_exception(self):
        e = AssertionError("I don't know much about art")

        def wrapper():
            class SpammySuite(TestSuite):
                def test_yogurt(self):
                    raise e

        wrapper()
        expect(self.test_failed_kwargs).to(contain_key_with_value("exception", e))

    def test_test_started_contains_test_name(self):
        def wrapper():
            class SpammySuite(TestSuite):
                def test_rosebud(self):
                    pass

        wrapper()
        expect(self.test_started_kwargs).to(contain_key_with_value("test_name", "test_rosebud"))

    def test_test_started_contains_suite_name(self):
        def wrapper():
            class SpammySuite(TestSuite):
                def test_rosebud(self):
                    pass

        wrapper()
        expect(self.test_started_kwargs).to(contain_key_with_value("suite_name", "SpammySuite"))

    def test_test_ended_contains_test_name(self):
        def wrapper():
            class SpammySuite(TestSuite):
                def test_rosebud(self):
                    pass

        wrapper()
        expect(self.test_ended_kwargs).to(contain_key_with_value("test_name", "test_rosebud"))

    def test_suite_erred_before_teardown_contains_exception(self):
        e = RuntimeError("I'm not quite dead")

        def wrapper():
            class SpammySuite(TestSuite):
                def setup_suite(self):
                    raise e

        wrapper()
        expect(self.suite_erred_kwargs).to(contain_key_with_value("exception", e))

    def test_suite_erred_during_teardown_contains_exception(self):
        e = RuntimeError("A moose bit my sister")

        def wrapper():
            class SpammySuite(TestSuite):
                def teardown_suite(self):
                    raise e

        wrapper()
        expect(self.suite_erred_kwargs).to(contain_key_with_value("exception", e))


if "__main__" == __name__:
    main()
