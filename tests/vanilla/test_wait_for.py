from expects import expect, be_a, be_above, be_false, equal
from time import sleep
from unittest import TestCase, main, skip

from twin_sister import TimeController, open_dependency_context

from questions_three.vanilla import wait_for


class SomeException(RuntimeError):
    pass


class TestWaitForExpectedCondition(TestCase):

    def setUp(self):
        self.context = open_dependency_context()

    def tearDown(self):
        self.context.close()

    def test_wait_for_retries(self):
        calls = 0
        timeout = 5
        throttle = 0.1

        def func():
            nonlocal calls
            calls += 1
            return False

        def do_it():
            wait_for(
                func=func,
                timeout=timeout,
                throttle=throttle
            )

        tc = TimeController(target=do_it)
        tc.start()
        tc.advance(seconds=timeout-0.1)
        last_check = calls
        sleep(2 * throttle)
        expect(calls).to(be_above(last_check))

    def test_wait_for_raises_timeout_error_if_timeout_exceeded(self):
        calls = 0
        timeout = 5
        throttle = 0.1

        def func():
            nonlocal calls
            calls += 1
            return False

        def do_it():
            wait_for(
                func=func,
                timeout=timeout,
                throttle=throttle
            )

        tc = TimeController(target=do_it)
        tc.start()
        tc.advance(seconds=timeout + 0.1)
        sleep(0.15)  # Give the thread a chance to cycle
        expect(tc.exception_caught).to(be_a(TimeoutError))

    def test_sleeps_for_specified_interval(self):
        throttle = 0.001
        slept_for = None

        def sleep_spy(n):
            nonlocal slept_for
            slept_for = n

        def do_it():
            return False

        self.context.inject(sleep, sleep_spy)
        try:
            wait_for(
                func=do_it,
                timeout=throttle*5,
                throttle=throttle
            )
        except TimeoutError:
            pass
        expect(slept_for).to(equal(throttle))

    def test_returns_none_when_condition_is_met(self):
        throttle = 0.001

        def func():
            return True

        def do_it():
            return wait_for(
                func=func,
                timeout=throttle * 5,
                throttle=throttle
            )

        response = do_it()
        expect(response).to(equal(None))


if __name__ == '__main__':
    main()
