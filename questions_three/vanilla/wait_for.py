from datetime import datetime, timedelta
import time

from twin_sister import dependency


def now():
    return dependency(datetime).now()


def wait_for(func, *, timeout, throttle):
    """
        Execute a function and retry if the return value is not truthy
        func -- (callable) Execute this.
        timeout -- (number) Raise TimeoutError after this number of seconds
        throttle -- (number) Wait this number of seconds between retries

        Return whatever func returns
        """
    sleep = dependency(time.sleep)
    expiry = now() + timedelta(seconds=timeout)
    while True:
        if func():
            return
        if now() > expiry:
            raise TimeoutError(f'Exceeded wait time of {timeout} seconds')
        sleep(throttle)
