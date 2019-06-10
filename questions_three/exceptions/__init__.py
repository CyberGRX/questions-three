class AuthenticationFailed(RuntimeError):
    pass


class InvalidConfiguration(RuntimeError):
    pass


class InvalidHttpResponse(RuntimeError):
    pass


class NoSuchRecord(RuntimeError):
    pass


class TooManyRedirects(RuntimeError):
    """
    HttpClient followed a 3xx redirect which led to another, and another...
    """


class TestSkipped(Exception):
    pass


class TooManyThings(RuntimeError):
    """
    Something contains more entities than expected
    """


class UndefinedEvent(Exception):
    """
    Something referenced a test event not defined in TestEvent
    """
