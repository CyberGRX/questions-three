from functools import partial
from unittest import TestCase, main

from expects import expect, be_empty, equal
from twin_sister.expects_matchers import complain
from twin_sister.fakes import FunctionSpy

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker


class TestMultiSubscribe(TestCase):
    def tearDown(self):
        EventBroker.reset()

    def test_requires_event_or_events(self):
        expect(partial(EventBroker.subscribe, func=lambda **k: None)).to(complain(TypeError))

    def test_event_and_events_are_mutually_exclusive(self):
        expect(
            partial(
                EventBroker.subscribe,
                event=TestEvent.test_started,
                events=(TestEvent.test_ended, TestEvent.test_erred),
                func=lambda **k: None,
            )
        ).to(complain(TypeError))

    def test_subscribes_to_first(self):
        all_events = list(TestEvent)
        events = (all_events[1], all_events[3], all_events[5])
        spy = FunctionSpy()
        EventBroker.subscribe(events=events, func=spy)
        EventBroker.publish(event=events[0])
        spy.assert_was_called()

    def test_subscribes_to_last(self):
        all_events = list(TestEvent)
        events = (all_events[1], all_events[3], all_events[5])
        spy = FunctionSpy()
        EventBroker.subscribe(events=events, func=spy)
        EventBroker.publish(event=events[-1])
        spy.assert_was_called()

    def test_does_not_subscribe_to_unspecified(self):
        all_events = list(TestEvent)
        events = (all_events[1], all_events[3], all_events[5])
        spy = FunctionSpy()
        EventBroker.subscribe(events=events, func=spy)
        EventBroker.publish(event=all_events[2])
        expect(spy.call_history).to(be_empty)

    def test_publishes_event_type(self):
        all_events = list(TestEvent)
        events = (all_events[1], all_events[3], all_events[5])
        published = events[1]
        spy = FunctionSpy()
        EventBroker.subscribe(events=events, func=spy)
        EventBroker.publish(event=published)
        expect(spy["event"]).to(equal(published))


if "__main__" == __name__:
    main()
