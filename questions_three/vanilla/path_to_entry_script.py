import os
import traceback


def path_to_entry_script():
    """
    Return the full path and filename of the script that was called from
    the command line, or None if the interpreter was launched without a
    script.
    """
    stack = traceback.extract_stack()
    if stack:
        fn = stack[0].filename
        if not fn.startswith('<'):
            return os.path.join(os.getcwd(), fn)
    return None
