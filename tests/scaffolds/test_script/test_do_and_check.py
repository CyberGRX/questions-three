from functools import partial
from unittest import TestCase, main

from expects import expect, equal
from twin_sister import close_all_dependency_contexts

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.scaffolds.test_script import do_and_check, skip


class TestDoAndCheck(TestCase):
    def setUp(self):
        close_all_dependency_contexts()
        EventBroker.reset()

    def test_executes_do_exactly_once(self):
        calls = 0

        def call():
            nonlocal calls
            calls += 1

        checks = (lambda: True, lambda: False, lambda: 42)
        do_and_check(do=call, checks=checks)
        expect(calls).to(equal(1))

    def test_executes_do_before_check(self):
        done = False
        checked = False

        def do():
            nonlocal done
            done = True

        def check():
            nonlocal checked
            assert done, "Do was not called"
            checked = True

        do_and_check(do=do, checks=(check,))
        assert checked, "Check was not called"

    def test_executes_all_checks(self):
        def make_check(n):
            nonlocal executed

            def check():
                executed.append(n)

            return check

        expected = 12
        executed = []
        do_and_check(do=lambda: True, checks=[make_check(n) for n in range(expected)])
        expect(executed).to(equal([n for n in range(expected)]))

    def test_executes_next_check_after_failure(self):
        called = False

        def first_check():
            assert False, "Intentional"

        def second_check():
            nonlocal called
            called = True

        do_and_check(do=lambda: True, checks=(first_check, second_check))
        assert called, "Second check was not run"

    def test_executes_next_check_after_error(self):
        called = False

        def first_check():
            raise RuntimeError("Intentional")

        def second_check():
            nonlocal called
            called = True

        do_and_check(do=lambda: True, checks=(first_check, second_check))
        assert called, "Second check was not run"

    def check_test_name(self, event, checker=None):
        published_name = None

        def do_something():
            pass

        def check_something():
            if checker:
                checker()

        def detect_start(test_name, **kwargs):
            nonlocal published_name
            published_name = test_name

        EventBroker.subscribe(event=event, func=detect_start)
        do_and_check(do=do_something, checks=(check_something,))
        expect(published_name).to(equal("do something and check something"))

    def test_starts_test_with_derived_name(self):
        self.check_test_name(TestEvent.test_started)

    def test_derived_name_includes_args(self):
        published_name = None

        def do_something():
            pass

        def check_something():
            pass

        def detect_start(test_name, **kwargs):
            nonlocal published_name
            published_name = test_name

        EventBroker.subscribe(event=TestEvent.test_started, func=detect_start)
        args = ("SPAM", "eggs", "sausage")
        do_and_check(do=do_something, checks=(partial(check_something, *args),))
        expect(published_name).to(equal("do something and check something with %s" % str(args)))

    def test_ends_test_with_derived_name(self):
        self.check_test_name(TestEvent.test_ended)

    def test_skips_test_with_derived_name(self):
        def func():
            skip("Skipped intentionally")

        self.check_test_name(TestEvent.test_skipped, checker=func)

    def test_fails_test_with_derived_name(self):
        def func():
            assert False, "intentional"

        self.check_test_name(TestEvent.test_failed, checker=func)

    def test_errs_test_with_derived_name(self):
        def func():
            raise RuntimeError("Intentional")

        self.check_test_name(TestEvent.test_erred, checker=func)

    def test_skips_all_checks_when_do_errs(self):
        expected = 7
        skipped = 0

        class FakeException(RuntimeError):
            pass

        def fail():
            raise FakeException("intentional")

        def count_skip(**kwargs):
            nonlocal skipped
            skipped += 1

        EventBroker.subscribe(event=TestEvent.test_skipped, func=count_skip)
        try:
            do_and_check(do=fail, checks=[lambda: n for n in range(expected)])
        except FakeException:
            pass
        expect(skipped).to(equal(expected))

    def test_re_raises_exception_from_do(self):
        raised = RuntimeError("But what have you done for me lately?")
        caught = None

        def do():
            raise raised

        try:
            do_and_check(do=do, checks=(lambda: True,))
        except Exception as e:
            caught = e
        expect(caught).to(equal(raised))


if "__main__" == __name__:
    main()
