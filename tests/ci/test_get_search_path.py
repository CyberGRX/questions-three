import sys
from unittest import TestCase, main

from expects import expect, equal
from twin_sister import open_dependency_context

from questions_three.ci.run_all.get_search_path import get_search_path


class TestGetSearchPath(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_logging=True)
        self.argv_stub = ["executable_name"]
        self.context.inject(sys.argv, self.argv_stub)

    def tearDown(self):
        self.context.close()

    def test_command_line_arg_trumps_environment(self):
        self.context.set_env(PATH_TO_TESTS="wrong")
        planted = "/T/which/sounds/like/p"
        self.argv_stub.append(planted)
        expect(get_search_path()).to(equal(planted))

    def test_environment_trumps_default(self):
        planted = "/somewhere/over/the/rainbow"
        self.context.set_env(PATH_TO_TESTS=planted)
        expect(get_search_path()).to(equal(planted))

    def test_default_is_cwd(self):
        expect(get_search_path()).to(equal("."))


if "__main__" == __name__:
    main()
