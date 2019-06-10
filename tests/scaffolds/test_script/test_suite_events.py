import logging
from unittest import TestCase, main

from expects import expect, be_empty, have_length, raise_error

from twin_sister import open_dependency_context

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from twin_sister.expects_matchers import contain_all_items_in, \
    contain_key_with_value
from questions_three.logging import logger_for_module
from questions_three.scaffolds \
    import disable_default_reporters, enable_default_reporters
from questions_three.scaffolds.test_script import test_suite
from twin_sister.fakes import EmptyFake


class FakeException(Exception):
    pass


class FakeBroker(EmptyFake):

    def __init__(self):
        self.messages = []

    def publish(self, **kwargs):
        self.messages.append(kwargs)


class FakeLog(EmptyFake):

    def __init__(self):
        super().__init__()
        self.errors = []

    def error(self, message):
        self.errors.append(message)

    def has_error_message(self, message):
        for msg in self.errors:
            if message in msg:
                return True
        return False


class TestSuiteEvents(TestCase):

    def setUp(self):
        disable_default_reporters()
        self.context = open_dependency_context()
        self.fake_broker = FakeBroker()
        self.context.inject(EventBroker, self.fake_broker)
        self.fake_log = FakeLog()
        self.context.inject(logging, self.fake_log)
        self.context.inject(logger_for_module, lambda m: self.fake_log)

    def tearDown(self):
        self.context.close()
        enable_default_reporters()

    def test_publishes_suite_started_with_suite_name_on_entry(self):
        name = 'Some Suite'
        with test_suite(name=name):
            pass
        expect(self.fake_broker.messages).not_to(be_empty)
        msg = self.fake_broker.messages[0]
        expect(msg).to(contain_all_items_in(
            {'event': TestEvent.suite_started, 'suite_name': name}))

    def test_publishes_suite_ended_with_suite_name_on_clean_exit(self):
        name = 'Another Suite'
        with test_suite(name=name):
            pass
        expect(self.fake_broker.messages).not_to(be_empty)
        msg = self.fake_broker.messages[-1]
        expect(msg).to(contain_all_items_in(
            {'event': TestEvent.suite_ended, 'suite_name': name}))

    def test_catches_suite_exception(self):
        def attempt():
            with test_suite(name='doomed'):
                raise Exception('intentional')
        expect(attempt).not_to(raise_error(Exception))

    def test_publishes_suite_ended_with_suite_name_on_unclean_exit(self):
        name = 'doomed'
        try:
            with test_suite(name=name):
                raise Exception('intentional')
        except Exception:
            pass  # Unexpected, but covered by another test
        expect(self.fake_broker.messages).not_to(be_empty)
        msg = self.fake_broker.messages[-1]
        expect(msg).to(contain_all_items_in(
            {'event': TestEvent.suite_ended, 'suite_name': name}))

    def test_publishes_suite_erred_with_suite_name_on_error(self):
        name = 'doomed'
        try:
            with test_suite(name=name):
                raise Exception('intentional')
        except Exception:
            pass  # Unexpected, but covered by another test
        expect(self.fake_broker.messages).not_to(be_empty)
        erred = [
            msg for msg in self.fake_broker.messages
            if msg['event'] == TestEvent.suite_erred]
        expect(erred).to(have_length(1))
        expect(erred[0]).to(contain_key_with_value('suite_name', name))

    def test_publishes_suite_erred_with_exception_on_error(self):
        expected = FakeException("That's impossible, even for a computer")
        try:
            with test_suite(name='spam'):
                raise expected
        except FakeException:
            pass  # Unexpected, but covered by another test
        erred = [
            msg for msg in self.fake_broker.messages
            if msg['event'] == TestEvent.suite_erred]
        expect(erred).to(have_length(1))
        expect(erred[0]).to(contain_key_with_value('exception', expected))


if '__main__' == __name__:
    main()
