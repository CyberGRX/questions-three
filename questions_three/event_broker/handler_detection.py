import re

from questions_three.constants import TestEvent
from questions_three.exceptions import UndefinedEvent

from .event_broker import EventBroker

EVENT_HANDLER_PATTERN = re.compile('^on_(.+)$')


def event_for_handler(handler_name):
    mat = EVENT_HANDLER_PATTERN.search(handler_name)
    if not mat:
        raise RuntimeError('Failed to parse %s' % handler_name)
    event = mat.group(1)
    if event in [e.name for e in TestEvent]:
        return TestEvent[mat.group(1)]
    raise UndefinedEvent('"%s" is not defined as a test event' % event)


def event_handler_names(obj):
    return [name for name in dir(obj) if name.startswith('on_')]


def subscribe_event_handlers(obj):
    """
    Detect event handlers in an object and subscribe each to its event.
    """
    for func_name in event_handler_names(obj):
        attr = getattr(obj, func_name)
        if hasattr(attr, '__call__'):
            EventBroker.subscribe(
                event=event_for_handler(func_name),
                func=getattr(obj, func_name))
