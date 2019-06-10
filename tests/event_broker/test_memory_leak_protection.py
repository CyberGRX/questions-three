import gc
import logging
from unittest import TestCase, main

from twin_sister import open_dependency_context

from questions_three.event_broker import EventBroker
from twin_sister.fakes import EmptyFake, MasterSpy

EVENT = 42


class Evidence:
    subscriber_ran = False


class Subscriber:

    def __init__(self):
        EventBroker.subscribe(event=EVENT, func=self.receiver)

    def receiver(self):
        Evidence.subscriber_ran = True


class TestMemoryLeakProtection(TestCase):

    def setUp(self):
        self.context = open_dependency_context()
        Evidence.subscriber_ran = False
        self.fake_log = MasterSpy(EmptyFake())
        self.context.inject(logging, self.fake_log)

    def tearDown(self):
        self.context.close()

    def test_bound_subscriber_gets_garbage_collected(self):
        # When the subscriber instantiates, it subscribes to an event
        # This causes the event broker to store a reference to the subscriber.
        # The test does not create a reference to the subscriber, so the broker
        # has the only reference.
        Subscriber()
        # Because the broker has the only reference, the subscriber should
        # be eligible for garbage collection.
        gc.collect()
        EventBroker.publish(event=EVENT)
        assert not Evidence.subscriber_ran, \
            'Subscriber ran after it should have been garbage collected'

    def test_unbound_subscriber_gets_garbage_collected(self):
        def subscriber():
            Evidence.subscriber_ran = True
        EventBroker.subscribe(event=EVENT, func=subscriber)
        subscriber = None
        gc.collect()
        EventBroker.publish(event=EVENT)
        assert not Evidence.subscriber_ran, \
            'Subscriber ran after it should have been garbage collected'

    def errors_logged(self):
        if self.fake_log.attribute_was_requested('error'):
            spy = self.fake_log.attribute_spies['error']
            return [args[0] for args, kwargs in spy.call_history]

    def test_does_not_attempt_to_run_garbage_collected_subscriber(self):
        def subscriber():
            pass
        EventBroker.subscribe(event=EVENT, func=subscriber)
        subscriber = None
        gc.collect()
        EventBroker.publish(event=EVENT)
        assert not self.errors_logged(), \
            'Unexpected errors in the log: "%s"' % (self.errors_logged())


if '__main__' == __name__:
    main()
