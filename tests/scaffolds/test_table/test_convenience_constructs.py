from unittest import TestCase, main

from expects import expect, be

import questions_three.scaffolds.common as common
import questions_three.scaffolds.test_table as test_table


class TestConvenienceConstructs(TestCase):
    def test_precondition_is_available_from_module(self):
        expect(test_table.precondition).to(be(common.precondition))

    def test_skip_is_available_from_module(self):
        expect(test_table.skip).to(be(common.skip))


if "__main__" == __name__:
    main()
