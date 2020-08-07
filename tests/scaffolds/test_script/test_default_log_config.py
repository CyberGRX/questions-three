import logging
from unittest import TestCase, main

from expects import expect
from twin_sister import close_all_dependency_contexts, open_dependency_context
from twin_sister.fakes import EmptyFake
from twin_sister.expects_matchers import contain_key_with_value

from questions_three.event_broker import EventBroker
from questions_three.logging.constants import MESSAGE_FORMAT
from questions_three.scaffolds import disable_default_reporters, enable_default_reporters
from questions_three.scaffolds.test_script import test_suite


class FakeLogging(EmptyFake):
    def __init__(self):
        super().__init__()
        self.config_history = []

    def basicConfig(self, *args, **kwargs):
        self.config_history.append((args, kwargs))


class TestDefaultLogConfig(TestCase):
    def setUp(self):
        close_all_dependency_contexts()
        disable_default_reporters()
        self.context = open_dependency_context(supply_fs=True)
        self.fake_logging = FakeLogging()
        self.context.inject(logging, self.fake_logging)
        EventBroker.reset()

    def tearDown(self):
        self.context.close()
        enable_default_reporters()

    def test_sets_level_info(self):
        with test_suite("spam"):
            pass
        args, kwargs = self.fake_logging.config_history[-1]
        expect(kwargs).to(contain_key_with_value("level", logging.INFO))

    def test_sets_expected_format(self):
        with test_suite("finland"):
            pass
        args, kwargs = self.fake_logging.config_history[-1]
        expect(kwargs).to(contain_key_with_value("format", MESSAGE_FORMAT))


if "__main__" == __name__:
    main()
