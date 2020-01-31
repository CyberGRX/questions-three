from expects import expect, equal
from questions_three.scaffolds.test_table import execute_test_table

TABLE = (
    ('x', 'y', 'expect sum', 'expect exception'),
    (2, 2, 4, None),
    (1, 0, 1, None),
    (0, 1, 0, None),
    (0.1, 0.1, 0.2, None),
    (1, 'banana', None, TypeError),
    (1, '1', None, TypeError),
    (2, 2, 5, None))


def test_add(*, x, y, expect_sum):
    expect(x + y).to(equal(expect_sum))


execute_test_table(
    suite_name='TestAddTwoThings', table=TABLE, func=test_add)
