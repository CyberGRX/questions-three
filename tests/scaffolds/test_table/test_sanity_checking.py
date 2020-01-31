from functools import partial
from unittest import TestCase, main

from expects import expect
from twin_sister.expects_matchers import complain

from questions_three.scaffolds.test_table import execute_test_table


class TestSanityChecking(TestCase):

    def test_complains_on_kwarg_name_mismatch(self):
        table = (
            ('one', 'two', 'three'),
            ('surprise', 'fear', 'ruthless efficiency'))

        def func(*, one, two, five):
            pass

        expect(
            partial(execute_test_table, func=func, table=table)).to(
                complain(TypeError))

    def test_kwarg_mismatch_check_not_tripped_up_by_local_variables(self):
        table = (
            ('one', 'two', 'three'),
            ('surprise', 'fear', 'ruthless efficiency'))

        def func(one, two):
            three = None
            three

        expect(
            partial(execute_test_table, func=func, table=table)).to(
                complain(TypeError))

    def test_complains_when_row_contains_too_few_columns(self):
        table = (
            ('one', 'two'),
            ('surprise', 'fear'))

        def func(one, two, three):
            pass

        expect(partial(execute_test_table, func=func, table=table)).to(
            complain(TypeError))

    def test_complains_when_row_contains_too_many_columns(self):
        table = (
            ('one', 'two', 'three'),
            ('surprise', 'fear', 'ruthless efficiency'))

        def func(one, two):
            pass

        expect(partial(execute_test_table, func=func, table=table)).to(
            complain(TypeError))

    def test_complains_if_two_rows_have_same_specified_test_name(self):
        table = (
            ('test name', 'thingy'),
            ('spam', 13),
            ('eggs', 14),
            ('sausage', 27),
            ('spam', 41))
        expect(
            partial(
                execute_test_table, func=lambda thingy: None,
                table=table)).to(
            complain(TypeError))

    def test_complains_if_two_rows_have_same_derived_test_name(self):
        table = (
            ('thing', 'number'),
            ('spam', 42),
            ('spam', 42))
        expect(
            partial(
                execute_test_table, func=lambda thing, number: None,
                table=table)).to(
            complain(TypeError))

    def test_complains_when_expect_exception_is_not_an_exception(self):
        table = (
            ('thing', 'expect exception'),
            (42, 'frog'))
        expect(
            partial(
                execute_test_table, table=table, func=lambda thing: None)).to(
            complain(TypeError))


if '__main__' == __name__:
    main()
