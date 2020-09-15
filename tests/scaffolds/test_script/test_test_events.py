from unittest import TestCase, main

from expects import expect, be_empty, have_length, raise_error
from twin_sister import open_dependency_context

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.exceptions import TestSkipped
from twin_sister.expects_matchers import contain_all_items_in, contain_key_with_value
from questions_three.logging import logger_for_module
from questions_three.scaffolds import disable_default_reporters, enable_default_reporters
from questions_three.scaffolds.test_script import test
from twin_sister.fakes import EmptyFake


class FakeException(Exception):
    pass


class FakeBroker(EmptyFake):
    def __init__(self):
        self.messages = []

    # Fake interface
    def message_for_event(self, event):
        msgs = [msg for msg in self.messages if msg["event"] == event]
        expect(msgs).to(have_length(1))
        return msgs[0]

    # Real interface
    def publish(self, **kwargs):
        self.messages.append(kwargs)


class FakeLog(EmptyFake):
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, message):
        self.errors.append(message)

    def warning(self, message):
        self.warnings.append(message)


class TestTestEvents(TestCase):
    def setUp(self):
        disable_default_reporters()
        self.context = open_dependency_context()
        self.fake_broker = FakeBroker()
        self.context.inject(EventBroker, self.fake_broker)
        self.fake_log = FakeLog()
        self.context.inject(logger_for_module, lambda m: self.fake_log)

    def tearDown(self):
        self.context.close()
        enable_default_reporters()

    def test_publishes_test_started_with_test_name_on_entry(self):
        name = "Shem"
        with test(name=name):
            pass
        expect(self.fake_broker.messages).not_to(be_empty)
        expect(self.fake_broker.messages[0]).to(
            contain_all_items_in({"event": TestEvent.test_started, "test_name": name})
        )

    def test_catches_exception(self):
        def attempt():
            with test(name="spam"):
                raise Exception("oops")

        expect(attempt).not_to(raise_error(Exception))

    def last_message(self):
        expect(self.fake_broker.messages).not_to(be_empty)
        return self.fake_broker.messages[-1]

    def test_publishes_test_ended_with_test_name_on_clean_exit(self):
        name = "Shem"
        with test(name=name):
            pass
        expect(self.last_message()).to(contain_all_items_in({"event": TestEvent.test_ended, "test_name": name}))

    def test_publishes_test_ended_with_test_name_on_exit_after_err(self):
        name = "something"
        try:
            with test(name=name):
                raise Exception("intentional")
        except Exception:
            pass  # Unexpected, but covered by another test
        expect(self.last_message()).to(contain_all_items_in({"event": TestEvent.test_ended, "test_name": name}))

    def test_publishes_test_ended_with_test_name_on_exit_after_fail(self):
        name = "something"
        try:
            with test(name=name):
                raise AssertionError("intentional")
        except Exception:
            pass  # Unexpected, but covered by another test
        expect(self.last_message()).to(contain_all_items_in({"event": TestEvent.test_ended, "test_name": name}))

    def test_publishes_test_ended_with_test_name_on_exit_after_skip(self):
        name = "something"
        try:
            with test(name=name):
                raise TestSkipped("intentional")
        except Exception:
            pass  # Unexpected, but covered by another test
        expect(self.last_message()).to(contain_all_items_in({"event": TestEvent.test_ended, "test_name": name}))

    def test_publishes_test_erred_with_test_name(self):
        name = "chump"
        try:
            with test(name=name):
                raise FakeException("intentional")
        except FakeException:
            pass  # unexpected but covered by another test
        expect(self.fake_broker.message_for_event(TestEvent.test_erred)).to(contain_key_with_value("test_name", name))

    def test_publishes_test_erred_with_exception(self):
        expected = FakeException("Seriously?")
        try:
            with test(name="something"):
                raise expected
        except FakeException:
            pass  # unexpected but covered by another test
        expect(self.fake_broker.message_for_event(TestEvent.test_erred)).to(
            contain_key_with_value("exception", expected)
        )

    def test_publishes_test_failed_with_test_name(self):
        name = "chump"
        try:
            with test(name=name):
                raise AssertionError("intentional")
        except AssertionError:
            pass  # unexpected but covered by another test
        expect(self.fake_broker.message_for_event(TestEvent.test_failed)).to(contain_key_with_value("test_name", name))

    def test_publishes_test_failed_with_exception(self):
        expected = AssertionError("coulda")
        try:
            with test(name="something"):
                raise expected
        except AssertionError:
            pass  # unexpected but covered by another test
        expect(self.fake_broker.message_for_event(TestEvent.test_failed)).to(
            contain_key_with_value("exception", expected)
        )

    def test_publishes_test_skipped_with_test_name(self):
        name = "skippy"
        try:
            with test(name=name):
                raise TestSkipped("I prefer not to")
        except TestSkipped:
            pass  # unexpected but covered by another test
        expect(self.fake_broker.message_for_event(TestEvent.test_skipped)).to(
            contain_key_with_value("test_name", name)
        )

    def test_publishes_test_skipped_with_exception(self):
        expected = TestSkipped("No way")
        try:
            with test(name="something"):
                raise expected
        except TestSkipped:
            pass  # unexpected but covered by another test
        expect(self.fake_broker.message_for_event(TestEvent.test_skipped)).to(
            contain_key_with_value("exception", expected)
        )


if "__main__" == __name__:
    main()
