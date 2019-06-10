from traceback import TracebackException


def indent(s):
    if s:
        spaces = 4 if s.startswith('File') or s.startswith('Traceback') else 8
        return ''.join([' ' for n in range(spaces)]) + s
    return ''


def format_exception(e):
    """
    Convert an exception to a human-readable message and stacktrace
    """
    tb = TracebackException.from_exception(e)
    stack = []
    for raw in tb.format():
        stack += [s.strip() for s in raw.split('\n')]
    msg = '(%s) %s' % ((type(e).__name__, e))
    trace = filter(lambda s: s, map(indent, [s for s in stack[:-1]]))
    return '{}\n'.format(msg) + '\n'.join(trace)
