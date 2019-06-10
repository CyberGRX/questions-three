from contextlib import contextmanager

from twin_sister import dependency

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.scaffolds.common.configure_logging \
    import configure_logging


@contextmanager
def test_suite(name):
    broker = dependency(EventBroker)
    configure_logging()
    broker.publish(event=TestEvent.suite_started, suite_name=name)
    try:
        yield
    except Exception as e:
        broker.publish(
            event=TestEvent.suite_erred, exception=e, suite_name=name)
    broker.publish(event=TestEvent.suite_ended, suite_name=name)
