import random
from unittest import TestCase, main

from expects import expect, equal
from twin_sister import open_dependency_context

from questions_three.scaffolds.test_table import execute_test_table


def deterministic_shuffle(original):
    original.reverse()


class TestRowRandomization(TestCase):

    def setUp(self):
        self.context = open_dependency_context(
            supply_env=True, supply_logging=True)
        self.context.inject(random.shuffle, deterministic_shuffle)

    def tearDown(self):
        self.context.close()

    def test_does_not_shuffle_by_default(self):
        executed_order = []
        table = (
            ('table row number',),
            (1,),
            (2,),
            (3,))

        def func(table_row_number):
            nonlocal executed_order
            executed_order.append(table_row_number)

        execute_test_table(table=table, func=func)
        expect(executed_order).to(equal([1, 2, 3]))

    def test_shuffles_rows_when_specified_true(self):
        executed_order = []
        table = (
            ('table row number',),
            (1,),
            (2,),
            (3,))

        def func(table_row_number):
            nonlocal executed_order
            executed_order.append(table_row_number)

        execute_test_table(
            table=table, func=func, randomize_order=True)
        expect(executed_order).to(equal([3, 2, 1]))

    def test_does_not_shuffle_rows_when_specified_false(self):
        executed_order = []
        table = (
            ('table row number',),
            (1,),
            (2,),
            (3,))

        def func(table_row_number):
            nonlocal executed_order
            executed_order.append(table_row_number)

        execute_test_table(
            table=table, func=func, randomize_order=False)
        expect(executed_order).to(equal([1, 2, 3]))


if '__main__' == __name__:
    main()
