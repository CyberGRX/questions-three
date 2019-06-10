from questions_three.scaffolds.common import skip

from .test import test


def funcname(f):
    return f.__name__.replace('_', ' ')


def identify(thing):
    attrs = dir(thing)
    if 'func' in attrs and 'args' in attrs:
        return '%s with %s' % (funcname(thing.func), thing.args)
    return funcname(thing)


def do_and_check(*, do, checks):
    """
    Perform one action, followed by a series of checks, each as its own test
    do (function): Execute this
    checks (sequence of functions): Execute each of these as its own test
    """
    err_from_do = None
    try:
        do()
    except Exception as e:
        err_from_do = e
    for check in checks:
        with test('%s and %s' % (identify(do), identify(check))):
            if err_from_do:
                skip('Skipping check because "do" function failed')
            else:
                check()
    if err_from_do:
        raise err_from_do
