from datetime import datetime, timedelta
import os
from time import sleep

from twin_sister import dependency

from questions_three.logging import logger_for_module
from questions_three.module_cfg import config_for_module

from .pool import Pool


log = logger_for_module(__name__)


def discover(top_dir):
    walk = dependency(os).walk
    scripts = []
    for path, _, files in walk(top_dir):
        scripts += [
            dependency(os).path.join(path, fn)
            for fn in files
            if not fn.startswith('_') and fn.endswith('.py')]
    return scripts


def _float_or_none(name, value):
    if value in (None, ''):
        return None
    try:
        return float(value)
    except ValueError as e:
        raise TypeError(
            f'Expected {name} ({value}) to be a number') from e


def run_all(path):
    """
    Run all tests beneath the given path
    """
    cfg = config_for_module(__name__)
    throttle = cfg.delay_between_checks_for_parallel_suite_completion
    limit = cfg.max_parallel_suites
    timeout = _float_or_none(
            name='$RUN_ALL_TIMEOUT', value=cfg.run_all_timeout)
    if timeout is None:
        expiry = None
    else:
        expiry = dependency(datetime).now() + timedelta(
            seconds=_float_or_none(
                name='$RUN_ALL_TIMEOUT', value=cfg.run_all_timeout))
    pool = Pool(limit)
    queue = list(discover(path))
    while queue:
        if expiry and dependency(datetime).now() > expiry:
            break
        while pool.has_capacity() and queue:
            pool.add(queue.pop(0))
        log.debug('Waiting in queue: %d' % len(queue))
        sleep(throttle)
    pool.wait_for_jobs(expiry=expiry)
    return pool.failure_count
