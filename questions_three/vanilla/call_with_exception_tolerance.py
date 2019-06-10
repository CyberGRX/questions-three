from datetime import datetime, timedelta
import time

from twin_sister import dependency


def now():
    return dependency(datetime).now()


def call_with_exception_tolerance(func, *, tolerate, timeout, throttle):
    """
    Execute a function and retry if a given exception is raised

    func -- (callable) Execute this.
    tolerate -- (Exception or sequence of Exception) Retry if this is raised
    timeout -- (number) Re-raise the exception after this number of seconds
    throttle -- (number) Wait this number of seconds between retries

    Return whatever func returns
    """
    # Convert all sequences to tuples so we can use them in an except statement
    if hasattr(tolerate, '__iter__'):
        tolerate = tuple(tolerate)
    sleep = dependency(time.sleep)
    expiry = now() + timedelta(seconds=timeout)
    while True:
        try:
            return func()
        except tolerate:
            if now() > expiry:
                raise
        sleep(throttle)
