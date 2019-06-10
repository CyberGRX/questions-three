from questions_three.exceptions import TestSkipped


def skip(message=None):
    raise TestSkipped(message)
