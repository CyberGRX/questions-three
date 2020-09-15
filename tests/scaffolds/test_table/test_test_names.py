from unittest import TestCase, main

from expects import expect, equal

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.scaffolds.test_table import execute_test_table


class TestTestNames(TestCase):
    def test_uses_test_name_when_supplied(self):
        rows = {"biggles": "surprise", "fang": "fear", "ximinez": "ruthless efficiency"}
        executed_tests = []
        executed_items = []
        table = [("test name", "item")]
        table += [(name, item) for name, item in rows.items()]

        def test_spy(*, test_name, **kwargs):
            nonlocal executed_tests
            executed_tests += [test_name]

        def row_func(*, item):
            nonlocal executed_items
            executed_items += [item]

        EventBroker.subscribe(event=TestEvent.test_started, func=test_spy)
        execute_test_table(table=table, func=row_func)
        expect(dict(zip(executed_tests, executed_items))).to(equal(rows))

    def test_uses_keyword_arguments_when_name_not_supplied(self):
        weapons = ("surprise", "fear", "ruthless efficiency")
        table = [("weapon",)]
        table += [(weapon,) for weapon in weapons]
        executed_tests = []
        executed_items = []

        def test_spy(*, test_name, **kwargs):
            nonlocal executed_tests
            executed_tests += [test_name]

        def row_func(*, weapon):
            nonlocal executed_items
            executed_items += [weapon]

        EventBroker.subscribe(event=TestEvent.test_started, func=test_spy)
        execute_test_table(table=table, func=row_func)
        expect(executed_tests).to(
            equal(["%s with %s" % (row_func.__name__, {"weapon": weapon}) for weapon in weapons])
        )
        expect(executed_items).to(equal(list(weapons)))


if "__main__" == __name__:
    main()
