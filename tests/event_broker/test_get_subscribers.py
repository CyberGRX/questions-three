import gc
from unittest import TestCase, main, skip

from expects import expect, equal

from questions_three.event_broker import EventBroker


def foo(**kwargs):
    pass


def bar(**kwargs):
    pass


def baz(**kwargs):
    pass


class TestGetSubscribers(TestCase):

    def setUp(self):
        EventBroker.reset()

    def test_returns_all_subscribers(self):
        EventBroker.subscribe(event=1, func=foo)
        EventBroker.subscribe(event=2, func=bar)
        EventBroker.subscribe(event=2, func=baz)
        expect(EventBroker.get_subscribers()).to(
            equal({foo, bar, baz}))

    def test_ignores_dead_references(self):
        EventBroker.subscribe(event=1, func=lambda: 1)
        EventBroker.subscribe(event=1, func=foo)
        gc.collect()
        expect(EventBroker.get_subscribers()).to(
            equal({foo}))


if '__main__' == __name__:
    main()
