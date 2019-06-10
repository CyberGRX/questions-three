class HttpError(RuntimeError):
    status_group = None
    status_code = None

    def __init__(self, *args, response=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.response = response


class HttpRedirect(HttpError):
    status_group = 3


class HttpMultipleChoices(HttpRedirect):
    status_code = 300


class HttpMovedPermanently(HttpRedirect):
    status_code = 301


class HttpFound(HttpRedirect):
    status_code = 302


class HttpSeeOther(HttpRedirect):
    status_code = 303


class HttpUseProxy(HttpRedirect):
    status_code = 305


class HttpTemporaryRedirect(HttpRedirect):
    status_code = 307


# https://tools.ietf.org/html/rfc7238
class PermanentRedirect(HttpRedirect):
    status_code = 308


class HttpClientError(HttpError):
    status_group = 4


class HttpBadRequest(HttpClientError):
    status_code = 400


class HttpUnauthorized(HttpClientError):
    status_code = 401


class HttpPaymentRequired(HttpClientError):
    status_code = 402


class HttpForbidden(HttpClientError):
    status_code = 403


class HttpNotFound(HttpClientError):
    status_code = 404


class HttpMethodNotAllowed(HttpClientError):
    status_code = 405


class HttpNotAcceptable(HttpClientError):
    status_code = 406


class HttpProxyAuthenticationRequired(HttpClientError):
    status_code = 407


class HttpRequestTimeout(HttpClientError):
    status_code = 408


class HttpConflict(HttpClientError):
    status_code = 409


class HttpGone(HttpClientError):
    status_code = 410


class HttpLengthRequired(HttpClientError):
    status_code = 411


class HttpPayloadTooLarge(HttpClientError):
    status_code = 413


class HttpUriTooLong(HttpClientError):
    status_code = 414


class HttpUnsupportedMediaType(HttpClientError):
    status_code = 415


class HttpExpectationFailed(HttpClientError):
    status_code = 417


class HttpImATeapot(HttpClientError):
    status_code = 418


class HttpUpgradeRequired(HttpClientError):
    status_code = 426


class HttpServerError(HttpError):
    status_group = 5


class HttpInternalServerError(HttpServerError):
    status_code = 500


class HttpNotImplemented(HttpServerError):
    status_code = 501


class HttpBadGateway(HttpServerError):
    status_code = 502


class HttpServiceUnavailable(HttpServerError):
    status_code = 503


class HttpGatewayTimeout(HttpServerError):
    status_code = 504


class HttpHttpVersionNotSupported(HttpServerError):
    status_code = 505
