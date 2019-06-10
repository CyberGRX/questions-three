from contextlib import contextmanager

from twin_sister import dependency

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.exceptions import TestSkipped


@contextmanager
def test(name):
    broker = dependency(EventBroker)
    broker.publish(event=TestEvent.test_started, test_name=name)
    try:
        yield
    except TestSkipped as e:
        broker.publish(
            event=TestEvent.test_skipped, test_name=name, exception=e)
    except AssertionError as e:
        broker.publish(
            event=TestEvent.test_failed, test_name=name, exception=e)
    except Exception as e:
        broker.publish(
            event=TestEvent.test_erred, test_name=name, exception=e)
    broker.publish(event=TestEvent.test_ended, test_name=name)
