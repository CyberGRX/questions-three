from unittest import TestCase, main

from expects import expect, equal
from questions_three.scaffolds.test_table import execute_test_table


class TestTableReading(TestCase):
    def test_converts_keyword_space_to_underscore(self):
        actual_value = None
        table = (("silly keyword",), ("silly value",))

        def test_func(silly_keyword):
            nonlocal actual_value
            actual_value = silly_keyword

        execute_test_table(func=test_func, table=table)
        expect(actual_value).to(equal("silly value"))


if "__main__" == __name__:
    main()
