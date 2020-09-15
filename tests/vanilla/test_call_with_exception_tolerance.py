from time import sleep
from unittest import TestCase, main

from expects import expect, be_above, equal
from twin_sister import TimeController, open_dependency_context

from twin_sister.expects_matchers import raise_ex
from questions_three.vanilla import call_with_exception_tolerance


class SpamException(RuntimeError):
    pass


class SonOfSpamException(SpamException):
    pass


class EggsException(RuntimeError):
    pass


class TestCallWithExceptionTolerance(TestCase):
    def setUp(self):
        self.context = open_dependency_context()

    def tearDown(self):
        self.context.close()

    def test_retries_up_to_specified_timeout(self):
        calls = 0
        timeout = 5
        throttle = 0.01

        def func():
            nonlocal calls
            calls += 1
            raise SpamException("intentional")

        def do_it():
            call_with_exception_tolerance(func=func, tolerate=SpamException, timeout=timeout, throttle=throttle)

        tc = TimeController(target=do_it)
        tc.start()
        tc.advance(seconds=timeout - 0.01)
        last_check = calls
        sleep(2 * throttle)
        expect(calls).to(be_above(last_check))

    def test_returns_whatever_the_function_returns(self):
        expected = 21345

        expect(
            call_with_exception_tolerance(func=lambda: expected, tolerate=SpamException, timeout=0.01, throttle=0)
        ).to(equal(expected))

    def test_re_raises_after_timeout(self):
        exception_class = SpamException

        def func():
            raise exception_class("intentional")

        def do_it():
            call_with_exception_tolerance(func=func, tolerate=SpamException, timeout=0.001, throttle=0)

        expect(do_it).to(raise_ex(exception_class))

    def test_raises_unspecified_exception_immediately(self):
        e = EggsException("intentional")
        calls = 0

        def func():
            nonlocal calls
            calls += 1
            raise e

        try:
            call_with_exception_tolerance(func=func, tolerate=SpamException, timeout=0.01, throttle=0)
        except EggsException:
            pass  # expected
        expect(calls).to(equal(1))

    def test_retries_exception_of_child_class(self):
        calls = 0

        def func():
            nonlocal calls
            calls += 1
            raise SonOfSpamException("intentional")

        try:
            call_with_exception_tolerance(func=func, tolerate=SpamException, timeout=0.01, throttle=0)
        except SonOfSpamException:
            pass  # expected
        expect(calls).to(be_above(1))

    def test_sleeps_for_specified_interval(self):
        throttle = 0.001
        slept_for = None

        def sleep_spy(n):
            nonlocal slept_for
            slept_for = n

        def complain():
            raise SpamException("intentional")

        self.context.inject(sleep, sleep_spy)
        try:
            call_with_exception_tolerance(
                func=complain, tolerate=SpamException, timeout=throttle * 5, throttle=throttle
            )
        except SpamException:
            pass
        expect(slept_for).to(equal(throttle))

    def test_does_not_tolerate_non_member_of_given_sequence(self):
        iterations = 0

        def attempt():
            nonlocal iterations
            iterations += 1
            raise EggsException()

        try:
            call_with_exception_tolerance(func=attempt, tolerate=(SpamException,), timeout=0.05, throttle=0)
        except EggsException:
            pass
        expect(iterations).to(equal(1))

    def test_tolerates_first_type_in_given_sequence(self):
        iterations = 0

        def attempt():
            nonlocal iterations
            iterations += 1
            raise SpamException()

        try:
            call_with_exception_tolerance(
                func=attempt, tolerate=(SpamException, EggsException), timeout=0.05, throttle=0
            )
        except SpamException:
            pass
        expect(iterations).to(be_above(1))

    def test_tolerates_last_type_in_given_sequence(self):
        iterations = 0

        def attempt():
            nonlocal iterations
            iterations += 1
            raise EggsException()

        try:
            call_with_exception_tolerance(
                func=attempt, tolerate=[SpamException, EggsException], timeout=0.05, throttle=0
            )
        except EggsException:
            pass
        expect(iterations).to(be_above(1))

    def test_tolerates_child_of_member_in_given_sequence(self):
        iterations = 0

        def attempt():
            nonlocal iterations
            iterations += 1
            raise SonOfSpamException()

        try:
            call_with_exception_tolerance(
                func=attempt, tolerate=(SpamException, EggsException), timeout=0.05, throttle=0
            )
        except SonOfSpamException:
            pass
        expect(iterations).to(be_above(1))


if "__main__" == __name__:
    main()
