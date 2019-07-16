from datetime import datetime, timedelta
from functools import partial
from io import StringIO
import os
from subprocess import PIPE, Popen, STDOUT
import sys
from time import sleep
from unittest import TestCase, main

from expects import expect, be_empty, contain, equal, have_length
from twin_sister import open_dependency_context

from questions_three.ci import run_all
from twin_sister.expects_matchers import contain_key_with_value


class FakeStream(StringIO):

    def read(self):
        return bytes(super().read(), encoding='utf-8')


class FakePopen:

    def __init__(self, complete=True, exit_code=0):
        self._is_started = False
        self._is_complete = complete
        self._exit_code = exit_code
        self.pid = 42
        self.stdout = FakeStream('')

    # Fake interface
    def fake_stdout(self, s):
        self.stdout = FakeStream(s)

    # Real interface
    def communicate(self):
        while not self._is_complete:
            pass
        return self._stdout, b''

    # Fake interface
    def is_running(self):
        return self._is_started and not self._is_complete

    # Fake interface
    def start(self):
        self._is_started = True

    # Fake interface
    def complete(self):
        self._is_complete = True

    # Real interface
    def poll(self):
        self.returncode = self._exit_code if self._is_complete else None
        return self.returncode

    # Real interface
    def wait(self, timeout=None):
        while not self._is_complete:
            pass
        self.returncode = self._exit_code
        return self.returncode


class FakePopenClass:

    def __init__(self):
        self.canned_objects = {}
        self.opened = []

    def __call__(self, args, **kwargs):
        # The spelling of args is intentional. We expect a sequence.
        # See standard library documentation for subprocess.Popen
        self.opened.append({'args': args, 'kwargs': kwargs})
        if len(args) > 1:
            script = args[1]
            if script in self.canned_objects.keys():
                obj = self.canned_objects[script]
                obj.start()
                return obj
        return FakePopen(complete=True)

    def scripts_executed(self):
        return [
            c['args'][1]
            for c in self.opened]


class TestRunAll(TestCase):

    def setUp(self):
        self.context = open_dependency_context(
            supply_fs=True, supply_env=True, supply_logging=True)
        self.context.set_env(
            DELAY_BETWEEN_CHECKS_FOR_PARALLEL_SUITE_COMPLETION=0,
            MAX_PARALLEL_SUITES=5)
        self.popen_class = FakePopenClass()
        self.context.inject(Popen, self.popen_class)

    def tearDown(self):
        self.context.close()

    def fake_file(self, filename):
        self.context.create_file(filename, content='')

    def test_runs_python_script_buried_in_specified_directory(self):
        path = 'spinach'
        filename = self.context.os.path.join(
            path, 'spam', 'eggs', 'sausage.py')
        self.fake_file(filename=filename)
        run_all(path)
        expect(self.popen_class.scripts_executed()).to(contain(filename))

    def test_uses_same_python_executable_as_self(self):
        expected = '/path/to/python'
        self.context.inject(sys.executable, expected)
        self.fake_file(filename='./whatever.py')
        run_all('.')
        opened = self.popen_class.opened
        expect(opened).to(have_length(1))
        expect(opened[0]['args'][0]).to(equal(expected))

    def test_does_not_run_non_python_script(self):
        path = 'the'
        unexpected = os.path.join(path, 'spinach', 'imposition')
        self.fake_file(filename=unexpected)
        run_all(path)
        expect(self.popen_class.scripts_executed()).not_to(contain(unexpected))

    def test_does_not_run_script_with_leading_underscore(self):
        path = 'the'
        unexpected = os.path.join(path, 'spinach', '_imposition.py')
        self.fake_file(filename=unexpected)
        run_all(path)
        expect(self.popen_class.scripts_executed()).not_to(contain(unexpected))

    def test_does_not_run_script_outside_specified_directory(self):
        self.fake_file(filename='/sir/not/appearing/in/this/film.py')
        run_all('/my_tests')
        expect(self.popen_class.scripts_executed()).to(be_empty)

    def test_runs_scripts_in_parallel(self):
        path = 'somewhere'
        first_script = os.path.join(path, 'script1.py')
        self.fake_file(first_script)
        p1 = FakePopen(complete=False)
        self.popen_class.canned_objects[first_script] = p1
        second_script = os.path.join(path, 'script2.py')
        self.fake_file(second_script)
        p2 = FakePopen(complete=False)
        self.popen_class.canned_objects[second_script] = p2
        t = self.context.create_time_controller(
            target=partial(run_all, path))
        t.start()
        expiry = datetime.now() + timedelta(seconds=0.1)
        while not(
                (p1.is_running() and p2.is_running()) or
                datetime.now() > expiry):
            sleep(0.01)
        try:
            assert p1.is_running(), 'First process is not running'
            assert p2.is_running(), 'Second process is not running'
        finally:
            # clean-up
            p1.complete()
            p2.complete()
            t.join()

    def set_limit(self, limit):
        self.context.set_env(MAX_PARALLEL_SUITES=limit)

    def test_limits_process_count_to_config(self):
        path = 'my_test_suites'
        limit = 3
        self.set_limit(limit)
        procs = {
            os.path.join(path, 'suite_%d.py' % n):
            FakePopen(complete=False)
            for n in range(limit + 2)}
        for filename, proc in procs.items():
            self.fake_file(filename)
            self.popen_class.canned_objects[filename] = proc
        t = self.context.create_time_controller(target=partial(run_all, path))
        t.start()
        sleep(0.1)
        running = 0
        for proc in procs.values():
            if proc.is_running():
                running += 1
        try:
            expect(running).to(equal(limit))
        finally:
            for proc in procs.values():
                proc.complete()
            t.join()

    def test_executes_next_script_when_worker_is_ready(self):
        self.set_limit(1)
        path = 'somewhere'
        script1 = os.path.join(path, 'one.py')
        p1 = FakePopen(complete=False)
        self.fake_file(script1)
        self.popen_class.canned_objects[script1] = p1
        script2 = os.path.join(path, 'two.py')
        p2 = FakePopen(complete=False)
        self.fake_file(script2)
        self.popen_class.canned_objects[script2] = p2
        t = self.context.create_time_controller(target=partial(run_all, path))
        t.start()
        sleep(0.1)
        try:
            assert p1.is_running(), 'P1 is not running'
            assert not p2.is_running(), 'P2 ran while P1 was still running'
            p1.complete()
            sleep(0.1)
            assert not p1.is_running(), 'P1 did not stop'
            assert p2.is_running(), 'P2 did not start'
        finally:
            p1.complete()
            p2.complete()
            t.join()

    def test_returns_0_when_all_exit_0(self):
        path = 'things/and/stuff'
        procs = {
            os.path.join(path, 'suite_%d.py' % n):
            FakePopen(complete=True, exit_code=0)
            for n in range(5)}
        for filename, proc in procs.items():
            self.fake_file(filename)
            self.popen_class.canned_objects[filename] = proc
        expect(run_all(path)).to(equal(0))

    def test_returns_non_zero_when_one_exits_non_zero(self):
        path = 'things/and/stuff'
        procs = {
            os.path.join(path, 'suite_%d.py' % n):
            FakePopen(complete=True, exit_code=0)
            for n in range(4)}
        procs[os.path.join(path, 'oops.py')] = FakePopen(
            complete=True, exit_code=1)
        for filename, proc in procs.items():
            self.fake_file(filename)
            self.popen_class.canned_objects[filename] = proc
        expect(run_all(path)).not_to(equal(0))

    def test_sends_stdout_to_pipe(self):
        path = 'things'
        filename = os.path.join(path, 'thing.py')
        self.fake_file(filename)
        run_all(path)
        opened = self.popen_class.opened
        expect(opened).to(have_length(1))
        expect(opened[0]['kwargs']).to(
            contain_key_with_value('stdout', PIPE))

    def test_pipes_stderr_to_stdout(self):
        path = 'things'
        filename = os.path.join(path, 'thing.py')
        self.fake_file(filename)
        run_all(path)
        opened = self.popen_class.opened
        expect(opened).to(have_length(1))
        expect(opened[0]['kwargs']).to(
            contain_key_with_value('stderr', STDOUT))

    def test_outputs_captured_stdout_on_proc_exit(self):
        expected = 'Our chief weapons are suprise, blah blah\n'
        unexpected = 'wrong!\n'
        spy = StringIO()
        self.context.inject(sys.stdout, spy)
        path = 'ximinez'
        proc = FakePopen(complete=False, exit_code=0)
        proc.fake_stdout(unexpected)
        filename = os.path.join(path, 'something.py')
        self.fake_file(filename)
        self.popen_class.canned_objects[filename] = proc
        t = self.context.create_time_controller(target=partial(run_all, path))
        t.start()
        sleep(0.05)
        proc.fake_stdout(expected)
        proc.complete()
        t.join()
        actual = spy.getvalue()
        expect(actual).not_to(contain(unexpected))
        expect(actual).to(contain(expected))

    def test_waits_for_all_to_exit(self):
        path = 'spamwhere'
        proc = FakePopen(complete=False)
        filename = os.path.join(path, 'spamthing.py')
        self.fake_file(filename)
        self.popen_class.canned_objects[filename] = proc
        t = self.context.create_time_controller(target=partial(run_all, path))
        t.start()
        sleep(0.1)
        try:
            assert t.is_alive(), 'Thread exited prematurely'
        finally:
            proc.complete()
            t.join()

    def test_logs_script_name_on_start(self):
        path = 'the'
        filename = os.path.join(path, 'rainbow.py')
        self.fake_file(filename)
        proc = FakePopen(complete=False)
        self.popen_class.canned_objects[filename] = proc
        t = self.context.create_time_controller(target=partial(run_all, path))
        t.start()
        sleep(0.1)
        messages = [rec.msg for rec in self.context.logging.stored_records]
        try:
            expect(messages).to(contain('Executing %s\n' % filename))
        finally:
            proc.complete()
            t.join()


if '__main__' == __name__:
    main()
