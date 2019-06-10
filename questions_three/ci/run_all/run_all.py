import os

from twin_sister import dependency

from questions_three.logging import logger_for_module
from questions_three.module_cfg import config_for_module

from .pool import Pool
from .queue_throttle import queue_throttle


DEFAULT_PROC_LIMIT = 1


log = logger_for_module(__name__)


def discover(top_dir):
    walk = dependency(os.walk)
    scripts = []
    for path, _, files in walk(top_dir):
        scripts += [
            os.path.join(path, fn)
            for fn in files
            if not fn.startswith('_') and fn.endswith('.py')]
    return scripts


def run_all(path):
    """
    Run all tests beneath the given path
    """
    wait = dependency(queue_throttle)
    cfg = config_for_module(__name__)
    config_limit = cfg.max_parallel_suites
    limit = int(config_limit) if config_limit else DEFAULT_PROC_LIMIT
    pool = Pool(limit)
    queue = list(discover(path))
    while queue:
        while pool.has_capacity() and queue:
            pool.add(queue.pop(0))
        log.debug('Waiting in queue: %d' % len(queue))
        wait()
    pool.wait_for_jobs()
    return pool.failure_count
