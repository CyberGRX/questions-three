from unittest import TestCase, main

from expects import expect, contain, raise_error
from twin_sister import open_dependency_context

from questions_three.event_broker import EventBroker
from questions_three.vanilla import format_exception


class TestExceptionHandling(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_logging=True)
        EventBroker.reset()

    def tearDown(self):
        self.context.close()

    def test_does_not_raise_exception_from_subscriber(self):
        def bad_subscriber(**kwargs):
            raise Exception("intentional walrus")

        event = "spamorama"
        EventBroker.subscribe(event=event, func=bad_subscriber)

        def attempt():
            EventBroker.publish(event=event)

        expect(attempt).not_to(raise_error(Exception))

    def test_logs_exception_from_subscriber(self):
        event = 42
        e = RuntimeError("I tried to think but nothing happened")

        def bad_subscriber(**kwargs):
            raise e

        EventBroker.subscribe(event=event, func=bad_subscriber)

        try:
            EventBroker.publish(event=event)
        except Exception:
            # We don't care whether an exception was thrown.
            # Another test covers that path.
            pass
        errors = [rec.msg for rec in self.context.logging.stored_records if rec.levelname == "ERROR"]
        expect(errors).to(contain(format_exception(e)))


if "__main__" == __name__:
    main()
