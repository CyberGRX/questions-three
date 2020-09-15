from unittest import TestCase, main

from expects import expect, have_length
from twin_sister.fakes import FunctionSpy

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.exceptions import TestSkipped
from questions_three.scaffolds.test_table import execute_test_table


class TestFlowControl(TestCase):
    def tearDown(self):
        EventBroker.reset()

    def test_advances_to_next_row_after_pass(self):
        table = (("thing",), ("spam",), ("eggs",), ("sausage",))
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_started, func=spy)

        def test_func(thing):
            pass

        execute_test_table(func=test_func, table=table)
        expect(spy.call_history).to(have_length(3))

    def test_advances_to_next_row_after_failure(self):
        table = (("thing",), ("spam",), ("eggs",), ("sausage",))
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_started, func=spy)

        def test_func(thing):
            assert False, "I told you so"

        execute_test_table(func=test_func, table=table)
        expect(spy.call_history).to(have_length(3))

    def test_advances_to_next_row_after_error(self):
        table = (("thing",), ("spam",), ("eggs",), ("sausage",))
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_started, func=spy)

        def test_func(thing):
            raise RuntimeError("Nobody expects the Spinach Imposition!")

        execute_test_table(func=test_func, table=table)
        expect(spy.call_history).to(have_length(3))
        pass

    def test_advances_to_next_row_after_skip(self):
        table = (("thing",), ("spam",), ("eggs",), ("sausage",))
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_started, func=spy)

        def test_func(thing):
            raise TestSkipped("I prefer not to")

        execute_test_table(func=test_func, table=table)
        expect(spy.call_history).to(have_length(3))
        pass


if "__main__" == __name__:
    main()
