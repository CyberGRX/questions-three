from unittest import TestCase, main

from expects import expect, equal
from twin_sister import open_dependency_context

from questions_three.exceptions import TestSkipped
from questions_three.scaffolds import disable_default_reporters, enable_default_reporters
from questions_three.scaffolds.xunit import TestSuite


class TestExecution(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_logging=True)
        disable_default_reporters()

    def tearDown(self):
        enable_default_reporters()
        self.context.close()

    def test_executes_setup_suite(self):
        ran = False

        def wrapper():
            class Suite(TestSuite):
                def setup_suite(self):
                    nonlocal ran
                    ran = True

        wrapper()
        assert ran, "Setup did not run"

    def test_makes_suite_setup_variables_available_to_tests(self):
        expected = 4588
        found = None

        def wrapper():
            class Suite(TestSuite):
                def setup_suite(self):
                    self.thing = expected

                def test_something(self):
                    nonlocal found
                    found = self.thing

        wrapper()
        expect(found).to(equal(expected))

    def test_executes_teardown_suite_if_no_failures(self):
        ran = False

        def wrapper():
            class Suite(TestSuite):
                def teardown_suite(self):
                    nonlocal ran
                    ran = True

        wrapper()
        assert ran, "Teardown did not run"

    def test_executes_teardown_suite_if_setup_suite_fails(self):
        ran = False

        def wrapper():
            class Suite(TestSuite):
                def setup_suite(self):
                    raise RuntimeError("intentional")

                def teardown_suite(self):
                    nonlocal ran
                    ran = True

        wrapper()
        assert ran, "Teardown did not run"

    def test_executes_teardown_suite_if_test_fails(self):
        ran = False

        def wrapper():
            class Suite(TestSuite):
                def test_boom(self):
                    raise AssertionError("intentional")

                def teardown_suite(self):
                    nonlocal ran
                    ran = True

        wrapper()
        assert ran, "Suite teardown did not run"

    def test_executes_first_test(self):
        ran = False

        def wrapper():
            class SandySuite(TestSuite):
                def test_spam(self):
                    nonlocal ran
                    ran = True

        wrapper()
        assert ran, "Test did not run"

    def test_does_not_execute_non_test(self):
        ran = False

        def wrapper():
            class Suite(TestSuite):
                def bestest(self):
                    nonlocal ran
                    ran = True

        wrapper()
        assert not ran, "Non-test ran"

    def test_executes_second_test(self):
        ran = False

        def wrapper():
            class Suite(TestSuite):
                def test_one(self):
                    pass

                def test_two(self):
                    nonlocal ran
                    ran = True

        wrapper()
        assert ran, "Second test did not run"

    def test_loses_state_between_tests(self):
        found = None
        initial_value = 0
        set_by_test_1 = 13

        def wrapper():
            class Suite(TestSuite):
                def setup_suite(self):
                    self.thing = initial_value

                def test_one(self):
                    self.thing = set_by_test_1

                def test_two(self):
                    nonlocal found
                    if "thing" in dir(self):
                        found = self.thing
                    else:
                        found = initial_value

        wrapper()
        expect(found).to(equal(initial_value))

    def test_executes_last_test(self):
        ran = False

        def wrapper():
            class Suite(TestSuite):
                def test_one(self):
                    pass

                def test_two(self):
                    pass

                def test_three(self):
                    pass

                def test_last(self):
                    nonlocal ran
                    ran = True

        wrapper()
        assert ran, "Last test did not run"

    def test_runs_next_test_if_test_fails(self):
        ran = False

        def wrapper():
            class Suite(TestSuite):
                def test_one(self):
                    raise AssertionError("oops")

                def test_two(self):
                    raise AssertionError("oops")

                def test_three(self):
                    raise AssertionError("oops")

                def test_last(self):
                    nonlocal ran
                    ran = True

        wrapper()
        assert ran, "Test did not run"

    def test_runs_next_test_if_test_errs(self):
        ran = False

        def wrapper():
            class Suite(TestSuite):
                def test_one(self):
                    raise RuntimeError("oops")

                def test_two(self):
                    raise RuntimeError("oops")

                def test_three(self):
                    raise RuntimeError("oops")

                def test_last(self):
                    nonlocal ran
                    ran = True

        wrapper()
        assert ran, "Test did not run"

    def test_runs_next_test_if_test_skips(self):
        ran = False

        def wrapper():
            class Suite(TestSuite):
                def test_one(self):
                    raise TestSkipped("oops")

                def test_two(self):
                    raise TestSkipped("oops")

                def test_three(self):
                    raise TestSkipped("oops")

                def test_last(self):
                    nonlocal ran
                    ran = True

        wrapper()
        assert ran, "Test did not run"

    def test_executes_setup_before_each_test(self):
        events = []

        def wrapper():
            class Suite(TestSuite):
                def setup(self):
                    nonlocal events
                    events.append("setup")

                def test1(self):
                    events.append("test")

                test2 = test1
                test3 = test1

        wrapper()
        expect(events).to(equal(["setup", "test", "setup", "test", "setup", "test"]))

    def test_executes_teardown_after_passing_test(self):
        events = []

        def wrapper():
            class Suite(TestSuite):
                def test1(self):
                    events.append("test")

                def teardown(self):
                    events.append("teardown")

        wrapper()
        expect(events).to(equal(["test", "teardown"]))

    def test_executes_teardown_after_failing_test(self):
        events = []

        def wrapper():
            class Suite(TestSuite):
                def test1(self):
                    events.append("test")
                    raise AssertionError("intentional")

                def teardown(self):
                    events.append("teardown")

        wrapper()
        expect(events).to(equal(["test", "teardown"]))

    def test_executes_teardown_after_skipped_test(self):
        events = []

        def wrapper():
            class Suite(TestSuite):
                def test1(self):
                    events.append("test")
                    raise RuntimeError("intentional")

                def teardown(self):
                    events.append("teardown")

        wrapper()
        expect(events).to(equal(["test", "teardown"]))


if "__main__" == __name__:
    main()
