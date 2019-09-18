from datetime import datetime
import logging
from logging import Logger, StreamHandler
from unittest import TestCase, main

from expects import expect, be_a, contain, end_with, equal, start_with
from twin_sister import open_dependency_context

from twin_sister.expects_matchers import raise_ex
from questions_three.logging import logger_for_module


class SpyHandler(StreamHandler):

    def __init__(self):
        self.level = logging.DEBUG
        self.messages = []

    def handle(self, record):
        self.messages.append(self.format(record))


class TestModuleLogger(TestCase):

    def setUp(self):
        self.context = open_dependency_context(
            supply_env=True, supply_logging=True)
        self.spy = SpyHandler()
        self.context.logging.StreamHandler = lambda *args, **kwrgs: self.spy

    def tearDown(self):
        self.context.close()

    def test_returns_a_logger(self):
        logger = logger_for_module(module_name='jimmy')
        expect(logger).to(be_a(Logger))

    def last_message(self):
        return self.spy.messages[-1]

    def test_logger_formatter_includes_log_level(self):
        logger = logger_for_module('something')
        logger.warning('SPAM ho!')
        expect(self.last_message().lower()).to(contain('warning'))

    def test_logger_formatter_includes_timestamp(self):
        logger = logger_for_module('something')
        logger.warning('SPAM ho!')
        expect(self.last_message()).to(
            start_with('%d-' % datetime.now().year))

    def test_logger_formatter_includes_module_name(self):
        name = 'names.ish_m_el'
        logger = logger_for_module(name)
        logger.info('Call me')
        expect(self.last_message()).to(contain(name))

    def test_logger_formatter_ends_with_message(self):
        msg = 'Hello!  My name is \'); DROP TABLE Users; --'
        logger = logger_for_module('something')
        logger.error(msg)
        expect(self.last_message()).to(end_with(msg))

    def test_default_log_level_is_info(self):
        logger = logger_for_module('something')
        expect(logger.level).to(equal(logging.INFO))

    def test_can_set_module_log_level_to_debug_via_environment(self):
        module_name = 'harvey'
        self.context.set_env(**{'%s_LOG_LEVEL' % module_name.upper(): 'DEBUG'})
        logger = logger_for_module(module_name)
        expect(logger.level).to(equal(logging.DEBUG))

    def test_can_set_module_log_level_to_warning_via_environment(self):
        module_name = 'jerry'
        self.context.set_env(
            **{'%s_LOG_LEVEL' % module_name.upper(): 'WARNING'})
        logger = logger_for_module(module_name)
        expect(logger.level).to(equal(logging.WARNING))

    def test_can_set_module_log_level_to_error_via_environment(self):
        module_name = 'bubba'
        self.context.set_env(**{'%s_LOG_LEVEL' % module_name.upper(): 'ERROR'})
        logger = logger_for_module(module_name)
        expect(logger.level).to(equal(logging.ERROR))

    def test_can_set_module_log_level_to_critical_via_environment(self):
        module_name = 'alt.barney.big.purple.dino_saur'
        self.context.set_env(
            **{'%s_LOG_LEVEL' % module_name.replace('.', '_').upper():
                'CRITICAL'})
        logger = logger_for_module(module_name)
        expect(logger.level).to(equal(logging.CRITICAL))

    def test_complains_about_environment_directive_with_unknown_level(self):
        module_name = 'alt.barney.big.purple.dino_saur'
        self.context.set_env(**{'%s_LOG_LEVEL' % module_name.replace(
                        '.', '_').upper(): 'BIGGLES'})

        def attempt():
            logger_for_module(module_name)

        expect(attempt).to(raise_ex(AttributeError))

    def test_environment_level_setting_affects_child_module(self):
        self.context.set_env(SPAM_EGGS_LOG_LEVEL='DEBUG')
        logger = logger_for_module(module_name='spam.eggs.sausage.spam')
        expect(logger.level).to(equal(logging.DEBUG))

    def test_child_setting_overrides_parent_setting(self):
        self.context.set_env(
            SPAM_EGGS_LOG_LEVEL='DEBUG',
            SPAM_EGGS_SAUSAGE_SPAM_LOG_LEVEL='WARNING')
        logger = logger_for_module(
            module_name='spam.eggs.sausage.spam')
        expect(logger.level).to(equal(logging.WARNING))

    def test_environment_level_setting_does_not_affect_other_module(self):
        self.context.set_env(ORANGES_LOG_LEVEL='CRITICAL')
        logger = logger_for_module(module_name='apples')
        expect(logger.level).to(equal(logging.INFO))


if '__main__' == __name__:
    main()
