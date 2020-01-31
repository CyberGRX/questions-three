from twin_sister import dependency

from questions_three.event_broker import subscribe_event_handlers
from questions_three.logging import logger_for_module
from questions_three.vanilla import format_exception


class EventLogger:

    def __init__(self):
        self._log = dependency(logger_for_module)(__name__)

    def activate(self):
        subscribe_event_handlers(self)

    def on_sample_measured(
             self, test_name, sample_parameters, sample_execution_seconds,
            **kwargs):
        self._log.info(
            f'{test_name} completed in {sample_execution_seconds} seconds')

    def on_suite_ended(self, suite_name, **kwargs):
        self._log.info('Suite "%s" ended' % suite_name)

    def on_suite_erred(self, exception=None, **kwargs):
        self._log.error(format_exception(exception))

    def on_suite_started(self, suite_name, **kwargs):
        self._log.info('Suite "%s" started' % suite_name)

    def on_test_ended(self, test_name, **kwargs):
        self._log.info('Check "%s" ended' % test_name)

    def on_test_erred(self, exception, **kwargs):
        self._log.error(format_exception(exception))

    def on_test_failed(self, test_name, exception, **kwargs):
        self._log.warning('Check "%s" failed: %s' % (test_name, exception))

    def on_test_skipped(self, test_name, exception, **kwargs):
        self._log.warning('Check "%s" skipped: %s' % (test_name, exception))

    def on_test_started(self, test_name, **kwargs):
        self._log.info('Check "%s" started' % test_name)
