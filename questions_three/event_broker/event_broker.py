from datetime import datetime
import weakref

from twin_sister import dependency

from questions_three.logging import logger_for_module
from questions_three.module_cfg import config_for_module
from questions_three.vanilla import format_exception


def call_if_alive(ref, **kwargs):
    func = ref()
    if func:
        func(**kwargs)


def current_time():
    return dependency(datetime).now()


def is_bound(func):
    return hasattr(func, '__self__') and func.__self__


class EventBroker:

    @classmethod
    def get_subscribers(cls):
        """
        Return a set containing all subscriber functions
        """
        found = set()
        for event, refs in cls._subscribers.items():
            found = found | set([r() for r in refs if r()])
        return found

    @classmethod
    def publish(cls, *, event, event_time=None, **kwargs):
        conf = config_for_module(__name__)
        run_id = conf.test_run_id
        if event_time is None:
            event_time = current_time()
        cls._logger.debug(event)
        if event in cls._subscribers.keys():
            for subscriber in cls._subscribers[event]:
                try:
                    call_if_alive(
                        subscriber, event_time=event_time,
                        run_id=run_id, **kwargs)
                except Exception as e:
                    cls._logger.error(format_exception(e))

    @classmethod
    def reset(cls):
        cls._subscribers = {}  # event -> [subscribers]
        cls._logger = logger_for_module(__name__)

    @classmethod
    def subscribe(cls, *, event, func):
        if event not in cls._subscribers.keys():
            cls._subscribers[event] = []
        if is_bound(func):
            subscriber = weakref.WeakMethod(func)
        else:
            subscriber = weakref.ref(func)
        cls._subscribers[event].append(subscriber)


EventBroker.reset()
