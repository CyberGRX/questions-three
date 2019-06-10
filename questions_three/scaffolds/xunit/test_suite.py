from .meta_suite import MetaSuite


class TestSuite(metaclass=MetaSuite):
    """
    The exposed part of a self-running xUnit test suite

    Test suites declare TestSuite as their parent class
    """
