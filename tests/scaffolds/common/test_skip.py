from unittest import TestCase, main

from expects import expect, contain, raise_error

from questions_three.exceptions import TestSkipped
from questions_three.scaffolds.common import skip


class TestSkip(TestCase):

    def test_raises_test_skipped(self):
        expect(skip).to(raise_error(TestSkipped))

    def test_uses_supplied_message(self):
        expected = "Why on earth would you want to do that?"
        try:
            skip(expected)
            assert False, 'No exception was raised'
        except TestSkipped as e:
            expect(str(e)).to(contain(expected))


if '__main__' == __name__:
    main()
