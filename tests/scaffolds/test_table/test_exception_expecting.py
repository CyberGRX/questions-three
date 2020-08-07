from unittest import TestCase, main

from expects import expect, be_empty, equal
from twin_sister.fakes import FunctionSpy

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.scaffolds.test_table import execute_test_table


class TestExceptionExpecting(TestCase):
    def tearDown(self):
        EventBroker.reset()

    def test_publishes_test_erred_when_different_exception_raised(self):
        table = (("expect exception",), (EOFError,))
        raised = ValueError()
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_erred, func=spy)

        def test_func():
            raise raised

        execute_test_table(table=table, func=test_func)
        expect(spy["exception"]).to(equal(raised))

    def test_exits_cleanly_when_expected_and_present(self):
        table = (("expect exception",), (ValueError,))
        raised = ValueError("a value error")
        spy = FunctionSpy()
        EventBroker.subscribe(events=(TestEvent.test_erred, TestEvent.test_failed, TestEvent.test_skipped), func=spy)

        def test_func():
            raise raised

        execute_test_table(table=table, func=test_func)
        expect(spy.call_history).to(be_empty)

    def test_publishes_test_failed_when_expected_and_absent(self):
        table = (("expect exception",), (ValueError,))
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_failed, func=spy)
        execute_test_table(table=table, func=lambda: None)
        spy.assert_was_called()


if "__main__" == __name__:
    main()
