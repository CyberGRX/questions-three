from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.exceptions import TestSkipped

from .runnable_suite import RunnableSuite


class TestRunner:
    def __init__(self, suite_name, suite_attributes, test_name):
        self.suite_name = suite_name
        self.suite_attributes = suite_attributes
        self.test_name = test_name

    def publish(self, event, **kwargs):
        EventBroker.publish(
            event=event, suite_name=self.suite_name,
            test_name=self.test_name, **kwargs)

    def run(self):
        self.publish(TestEvent.test_started)
        clean_suite = RunnableSuite(attrs=self.suite_attributes)
        try:
            clean_suite.run_one_test(test_name=self.test_name)
        except TestSkipped as e:
            self.publish(TestEvent.test_skipped, exception=e)
        except AssertionError as e:
            self.publish(TestEvent.test_failed, exception=e)
        except Exception as e:
            self.publish(TestEvent.test_erred, exception=e)
        self.publish(TestEvent.test_ended)
