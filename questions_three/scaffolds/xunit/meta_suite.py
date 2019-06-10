from .suite_runner import SuiteRunner


class MetaSuite(type):

    def __new__(cls, name, parents, dct):
        # Don't treat the base class like a suite
        if 'TestSuite' != name:
            SuiteRunner(suite_name=name, suite_attributes=dct).run()
        return type.__new__(cls, name, parents, dct)
