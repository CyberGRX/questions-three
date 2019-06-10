"""
Due to some hocus-pocus which you can learn from the source code,
simply declaring the class causes the test to run, so this file
is a plain-old python executable.
"""
from questions_three.scaffolds.xunit import TestSuite, skip


class MyXunitSuite(TestSuite):

    def setup_suite(self):
        """
        Perform setup that affects all tests here
        Changes to "self" will affect all tests.
        """
        print('This runs once at the start of the suite')

    def teardown_suite(self):
        print('This runs once at the end of the suite')

    def setup(self):
        """
        Perform setup for each test here.
        Changes to "self" will affect the current test only.
        """
        print('This runs before each test')

    def teardown(self):
        print('This runs after each test')

    def test_that_passes(self):
        """
        The method name is xUnit magic.
        Methods named "test..." get treated as test cases.
        """
        print('This test passes')

    def test_that_fails(self):
        print('This test fails')
        assert False, 'I failed'

    def test_that_errs(self):
        print('This test errs')
        raise RuntimeError('I tried to think but nothing happened')

    def test_that_skips(self):
        print('This test skips')
        skip("Don't do that")
