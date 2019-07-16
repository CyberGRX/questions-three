from functools import partial
from subprocess import Popen
from time import sleep
from unittest import TestCase, main

from expects import be_a, be_none, expect, have_length
from questions_three.vanilla import format_exception
from twin_sister import open_dependency_context
from twin_sister.expects_matchers import complain
from twin_sister.fakes import EmptyFake, FunctionSpy

from questions_three.ci.run_all.run_all import run_all


class TestRunAllTimeout(TestCase):

    def setUp(self):
        self.context = open_dependency_context(
            supply_env=True, supply_fs=True, supply_logging=True)
        self.context.set_env(
            DELAY_BETWEEN_CHECKS_FOR_PARALLEL_SUITE_COMPLETION=0)
        self.fake_process = EmptyFake()
        self.context.inject_as_class(Popen, self.fake_process)
        self.pretend_process_is_running()

    def tearDown(self):
        self.context.close()

    def pretend_process_is_running(self):
        self.fake_process.poll = lambda: None

    def pretend_process_is_stopped(self):
        self.fake_process.poll = lambda: 0

    def exercise_sut(self):
        bogus_path = self.context.os.path.join('some', 'where')
        self.context.fs.create_dir(bogus_path)
        bogus_script = self.context.os.path.join(bogus_path, 'something.py')
        self.context.fs.create_file(bogus_script)
        run_all(bogus_path)

    def test_does_not_time_out_if_unset(self):
        tc = self.context.create_time_controller(target=self.exercise_sut)
        tc.start()
        tc.advance(days=70)
        sleep(0.05)
        expect(tc.exception_caught).to(be_none)
        assert tc.is_alive(), 'run_all terminated unexpectedly'
        self.pretend_process_is_stopped()
        tc.join()

    def test_does_not_time_out_if_empty_string(self):
        self.context.set_env(RUN_ALL_TIMEOUT='')
        tc = self.context.create_time_controller(target=self.exercise_sut)
        tc.start()
        sleep(0.05)
        tc.advance(hours=72)
        sleep(0.05)
        if tc.exception_caught is not None:
            raise AssertionError(format_exception(tc.exception_caught))
        assert tc.is_alive(), 'Exited prematurely'
        self.pretend_process_is_stopped()
        tc.join()

    def test_complains_if_non_numeric(self):
        self.context.set_env(RUN_ALL_TIMEOUT='peach')
        expect(partial(run_all, 'whatever')).to(
            complain(TypeError))

    def test_does_not_time_out_before_limit(self):
        limit = 42
        self.context.set_env(RUN_ALL_TIMEOUT=limit)
        tc = self.context.create_time_controller(target=self.exercise_sut)
        tc.start()
        tc.advance(seconds=limit-0.01)
        expect(tc.exception_caught).to(be_none)
        assert tc.is_alive(), 'Exited prematurely'
        self.pretend_process_is_stopped()
        tc.join()

    def test_times_out_after_limit(self):
        limit = 42
        self.context.set_env(RUN_ALL_TIMEOUT=limit)
        tc = self.context.create_time_controller(target=self.exercise_sut)
        tc.start()
        sleep(0.05)
        tc.advance(seconds=limit+1)
        sleep(0.05)
        self.pretend_process_is_stopped()
        expect(tc.exception_caught).to(be_a(TimeoutError))
        tc.join()

    def test_times_out_when_suites_remain_in_queue_after_expiry(self):
        limit = 42
        self.context.set_env(
            MAX_PARALLEL_SUITES=1, RUN_ALL_TIMEOUT=limit)
        bogus_path = self.context.os.path.join('some', 'where')
        self.context.fs.create_dir(bogus_path)
        for bogus_script in ('something.py', 'or_other.py'):
            self.context.create_file(
                self.context.os.path.join(bogus_path, bogus_script))
        tc = self.context.create_time_controller(
            target=partial(run_all, bogus_path))
        tc.start()
        sleep(0.05)
        tc.advance(seconds=limit+1)
        sleep(0.05)
        expect(tc.exception_caught).to(be_a(TimeoutError))
        self.pretend_process_is_stopped()
        tc.join()

    def test_kills_running_procs(self):
        limit = 42
        self.context.set_env(RUN_ALL_TIMEOUT=limit)
        spy = FunctionSpy()
        self.fake_process.kill = spy
        tc = self.context.create_time_controller(target=self.exercise_sut)
        tc.start()
        sleep(0.05)
        tc.advance(seconds=limit+1)
        sleep(0.05)
        expect(spy.call_history).to(have_length(1))
        self.pretend_process_is_stopped()
        tc.join()


if '__main__' == __name__:
    main()
