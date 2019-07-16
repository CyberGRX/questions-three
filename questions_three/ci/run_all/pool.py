from datetime import datetime
import sys
from time import sleep

from questions_three.logging import logger_for_module
from questions_three.module_cfg import config_for_module
from twin_sister import dependency

from .job import Job


class Pool:

    def __init__(self, limit):
        self._limit = limit
        self._running = []
        self._log = dependency(logger_for_module)(__name__)
        self._stdout = dependency(sys.stdout)
        self.failure_count = 0

    def _prune(self):
        running = []
        for job in self._running:
            exit_code = job.poll()
            if exit_code is None:
                running.append(job)
            elif exit_code > 0:
                self.failure_count += 1
        self._running = running
        self._log.debug('In progress: %s' % str([job.name for job in running]))

    def add(self, suite_filename):
        self._log.info('Executing %s\n' % suite_filename)
        job = Job(path_to_script=suite_filename, output_stream=self._stdout)
        job.run()
        self._running.append(job)

    def _kill_jobs(self):
        for job in self._running:
            job.kill()

    def wait_for_jobs(self, *, expiry):
        cfg = config_for_module(__name__)
        throttle = cfg.delay_between_checks_for_parallel_suite_completion
        while self._running:
            if expiry and dependency(datetime).now() > expiry:
                self._kill_jobs()
                raise TimeoutError('Tests ran longer than the configured limit')
            sleep(throttle)
            self._prune()

    def has_capacity(self):
        self._prune()
        return self._limit is None or len(self._running) < self._limit
