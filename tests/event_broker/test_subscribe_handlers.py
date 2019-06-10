from unittest import TestCase, main, skip

from expects import expect, raise_error

from questions_three.constants import TestEvent
from questions_three.exceptions import UndefinedEvent
from questions_three.event_broker import EventBroker, \
    subscribe_event_handlers


class TestSubscribEventHandlers(TestCase):

    def setUp(self):
        EventBroker.reset()

    def test_subscribes_recognized_handler_to_matching_event(self):
        class Thing:
            def __init__(self):
                self.was_called = False

            def on_test_skipped(self, **kwargs):
                self.was_called = True

        thing = Thing()
        subscribe_event_handlers(thing)
        EventBroker.publish(event=TestEvent.test_skipped)
        assert thing.was_called, 'Subscriber was not called'

    def test_complains_about_unrecognized_handler(self):
        class Thing:
            def on_spam_slung_sluggishly(self, **kwargs):
                pass

        def attempt():
            subscribe_event_handlers(Thing())

        expect(attempt).to(raise_error(UndefinedEvent))

    def test_ignores_non_function(self):
        class Thing:
            on_not_a_function = True

        def attempt():
            subscribe_event_handlers(Thing())
        expect(attempt).not_to(raise_error(UndefinedEvent))

    def test_ignores_method_not_starting_with_on(self):
        class Thing:
            def __init__(self):
                self.was_called = False

            def test_skipped(self, **kwargs):
                self.was_called = True

        thing = Thing()
        subscribe_event_handlers(thing)
        EventBroker.publish(event=TestEvent.test_skipped)
        assert not thing.was_called, 'Handler was detected inapproprately'


if '__main__' == __name__:
    main()
