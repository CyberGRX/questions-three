from unittest import TestCase, main

from expects import expect, be

from questions_three.scaffolds.check_script import check, check_suite
from questions_three.scaffolds.test_script import test, test_suite


class TestAliases(TestCase):
    def test_check_suite(self):
        expect(check_suite).to(be(test_suite))

    def test_check(self):
        expect(check).to(be(test))


if "__main__" == __name__:
    main()
