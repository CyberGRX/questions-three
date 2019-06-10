from datetime import datetime, timedelta
from unittest import TestCase, main

from expects import expect
from twin_sister import open_dependency_context

from questions_three.event_broker import EventBroker
from twin_sister.expects_matchers import contain_key_with_value
from twin_sister.fakes import EmptyFake


class Subscriber:

    def __init__(self, event):
        self.kwargs_received = None
        EventBroker.subscribe(event=event, func=self.receiver)

    def receiver(self, **kwargs):
        self.kwargs_received = kwargs


class TestEventAutoTime(TestCase):

    def setUp(self):
        EventBroker.reset()
        self.context = open_dependency_context()
        self.fake_now = datetime.fromtimestamp(1515429469.61845)
        self.fake_datetime_module = EmptyFake()
        self.fake_datetime_module.now = lambda: self.fake_now
        self.context.inject(datetime, self.fake_datetime_module)

    def tearDown(self):
        self.context.close()

    def test_adds_current_time_if_no_time_specified(self):
        event = "A sale at Penny's!"
        subscriber = Subscriber(event=event)
        EventBroker.publish(event=event)
        expect(subscriber.kwargs_received).to(
            contain_key_with_value('event_time', self.fake_now))

    def test_uses_given_time_if_specified(self):
        event = 12
        expected = self.fake_now + timedelta(minutes=42)
        subscriber = Subscriber(event=event)
        EventBroker.publish(event=event, event_time=expected)
        expect(subscriber.kwargs_received).to(
            contain_key_with_value('event_time', expected))


if '__main__' == __name__:
    main()
