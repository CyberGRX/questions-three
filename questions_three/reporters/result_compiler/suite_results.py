class TestResult:

    def __init__(self, test_name):
        self.artifacts = []
        self.end_time = None
        self.exception = None
        self.name = test_name
        self.start_time = None
        self.status = None


class SuiteResults:

    def __init__(self):
        self.artifacts = []
        self.suite_end_time = None
        self.suite_exception = None
        self.suite_name = None
        self.suite_start_time = None
        self.tests = []
