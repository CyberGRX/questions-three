from questions_three.constants import TestEvent
from questions_three.exceptions import TestSkipped
from questions_three.event_broker import EventBroker
from questions_three.scaffolds.common.activate_reporters \
    import activate_reporters
from questions_three.scaffolds.common.configure_logging \
    import configure_logging

from .runnable_suite import RunnableSuite
from .test_runner import TestRunner


class SuiteRunner:

    def __init__(self, suite_name, suite_attributes):
        self.suite_name = suite_name
        self.suite_attributes = suite_attributes
        configure_logging()
        activate_reporters()

    def discover_tests(self):
        return [
            k for k, v in self.suite_attributes.items()
            if k.startswith('test')]

    def publish(self, event, **kwargs):
        EventBroker.publish(event=event, suite_name=self.suite_name, **kwargs)

    def run(self):
        self.publish(TestEvent.suite_started)
        stateful_suite = RunnableSuite(self.suite_attributes)
        suite_erred = False
        suite_skipped_exception = None
        try:
            stateful_suite.setup_suite()
        except TestSkipped as e:
            suite_skipped_exception = e
        except Exception as e:
            self.publish(TestEvent.suite_erred, exception=e)
            suite_erred = True
        for test_name in self.discover_tests():
            if suite_erred:
                self.publish(
                    TestEvent.test_skipped, test_name=test_name,
                    exception=TestSkipped('Suite setup failed'))
            elif suite_skipped_exception:
                self.publish(
                    TestEvent.test_skipped, test_name=test_name,
                    exception=suite_skipped_exception)
            else:
                TestRunner(
                    suite_name=self.suite_name,
                    suite_attributes=dict(
                        self.suite_attributes,
                        **stateful_suite.get_suite_context()),
                    test_name=test_name).run()
        try:
            if not suite_skipped_exception:
                stateful_suite.teardown_suite()
        except Exception as e:
            self.publish(TestEvent.suite_erred, exception=e)
        self.publish(TestEvent.suite_ended)
