from datetime import datetime
import weakref

from twin_sister import dependency

from questions_three.logging import logger_for_module
from questions_three.module_cfg import config_for_module
from questions_three.vanilla import format_exception


def call_if_alive(ref, **kwargs):
    log = logger_for_module(__name__)
    func = ref()
    if func:
        log.debug(f'Executing {func}')
        try:
            func(**kwargs)
            log.debug(f'{func} exited cleanly')
        except Exception as e:
            log.error(format_exception(e))


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
        log = logger_for_module(__name__)
        run_id = conf.test_run_id
        if event_time is None:
            event_time = current_time()
        log.debug(event)
        if event in cls._subscribers.keys():
            for subscriber in cls._subscribers[event]:
                call_if_alive(
                    subscriber, event=event, event_time=event_time,
                    run_id=run_id, **kwargs)

    @classmethod
    def reset(cls):
        cls._subscribers = {}  # event -> [subscribers]

    @classmethod
    def _subscribe(cls, *, func, event):
        if event not in cls._subscribers.keys():
            cls._subscribers[event] = []
        if is_bound(func):
            subscriber = weakref.WeakMethod(func)
        else:
            subscriber = weakref.ref(func)
        cls._subscribers[event].append(subscriber)

    @classmethod
    def subscribe(cls, *, func, event=None, events=None):
        if not (bool(event) ^ bool(events)):
            raise TypeError(
                'An event or events must be specified (but not both)')
        if events:
            for event in events:
                cls._subscribe(func=func, event=event)
        else:
            cls._subscribe(func=func, event=event)


EventBroker.reset()
