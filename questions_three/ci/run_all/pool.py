import sys

from questions_three.logging import logger_for_module
from twin_sister import dependency

from .job import Job
from .queue_throttle import queue_throttle


class Pool:

    def __init__(self, limit):
        self._limit = limit
        self._running = []
        self._log = dependency(logger_for_module)(__name__)
        self._stdout = dependency(sys.stdout)
        self._throttle = dependency(queue_throttle)
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

    def wait_for_jobs(self):
        while self._running:
            self._throttle()
            self._prune()

    def has_capacity(self):
        self._prune()
        return self._limit is None or len(self._running) < self._limit
