from unittest import TestCase, main

from expects import expect, be_empty, have_length

from questions_three.event_broker import EventBroker
from twin_sister.expects_matchers import contain_all_items_in


class Subscriber:
    def __init__(self, event=None):
        self.received = []
        if event:
            self.subscribe(event)

    def subscribe(self, event):
        EventBroker.subscribe(event=event, func=self.receive)

    def receive(self, **kwargs):
        self.received.append(kwargs)


class TestPublishAndSubscribe(TestCase):
    def setUp(self):
        EventBroker.reset()

    def test_first_subscriber_receives_message_on_expected_event(self):
        subscriber = Subscriber()
        event = "cabbages"
        subscriber.subscribe(event)
        EventBroker.publish(event=event)
        expect(subscriber.received).to(have_length(1))

    def test_third_subscriber_receives_message_on_expected_event(self):
        event = "kings"
        subscribers = [Subscriber(event) for n in range(3)]
        EventBroker.publish(event=event)
        expect(subscribers[2].received).to(have_length(1))

    def test_subscriber_does_not_receive_message_on_unexpected_event(self):
        expected_event = "the larch"
        unexpected_event = "the spinach imposition"
        subscriber = Subscriber(expected_event)
        EventBroker.publish(event=unexpected_event)
        expect(subscriber.received).to(have_length(0))

    def test_subscriber_receives_arbitrary_keyword_arguments(self):
        kwargs = {"spam": 42, "eggs": (1, 2, 3, 4, 5), "beans": "off"}
        event = "dance"
        subscriber = Subscriber(event)
        EventBroker.publish(event=event, **kwargs)
        received = subscriber.received
        expect(received).not_to(be_empty)
        expect(received[-1]).to(contain_all_items_in(kwargs))

    def test_after_reset_old_subscriber_does_not_receive_message(self):
        event = 2
        subscriber = Subscriber(event)
        EventBroker.reset()
        EventBroker.publish(event=event)
        expect(subscriber.received).to(be_empty)

    def test_after_reset_new_subscriber_receives_message(self):
        event = 2
        EventBroker.reset()
        subscriber = Subscriber(event)
        EventBroker.publish(event=event)
        expect(subscriber.received).not_to(be_empty)


if "__main__" == __name__:
    main()
