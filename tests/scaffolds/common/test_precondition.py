from unittest import TestCase, main

from expects import expect, raise_error

from questions_three.exceptions import TestSkipped
from questions_three.scaffolds.common import precondition


class TestPrecondition(TestCase):

    def test_raises_test_skipped_if_false(self):
        def attempt():
            precondition(False)
        expect(attempt).to(raise_error(TestSkipped))

    def test_raises_nothing_if_true(self):
        def attempt():
            precondition(True)
        expect(attempt).not_to(raise_error(Exception))


if '__main__' == __name__:
    main()
