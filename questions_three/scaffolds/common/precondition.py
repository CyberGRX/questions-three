from questions_three.exceptions import TestSkipped


def precondition(statement):
    """
    Raise TestSkipped if statement is false
    """
    if not statement:
        raise TestSkipped('Skipping test because precondition is not met')
