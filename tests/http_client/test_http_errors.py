from unittest import TestCase, main

from expects import expect, be, contain
import requests
from twin_sister import open_dependency_context

from twin_sister.expects_matchers import raise_ex
from twin_sister.fakes import EndlessFake
import questions_three.exceptions.http_error as error
from questions_three.http_client import HttpClient


HttpError = error.HttpError


class FakeHttpResponse(EndlessFake):

    def __init__(self):
        super().__init__()
        self.status_code = 200
        self.text = ''


class FakeRequests:

    def __init__(self, response):
        self.response = response

    def __getattr__(self, name):
        return lambda *args, **kwargs: self.response


def send_get():
    HttpClient().get('stuffed')


class TestHttpErrors(TestCase):

    def setUp(self):
        self.context = open_dependency_context()
        self.response = FakeHttpResponse()
        self.context.inject(requests, FakeRequests(response=self.response))

    def tearDown(self):
        self.context.close()

    def test_exception_contains_response(self):
        self.response.status_code = 400
        try:
            HttpClient().get('http://something')
        except HttpError as e:
            caught = e
        expect(caught.response).to(be(self.response))

    def test_exception_msg_contains_reponse_body(self):
        expected = "If you don't know, I'm certainly not going to tell you."
        self.response.status_code = 400
        self.response.text = expected
        try:
            HttpClient().get('http://whatever')
            raise AssertionError('No exception was raised')
        except HttpError as e:
            caught = e
        expect(str(caught)).to(contain(expected))

    def test_covers_delete(self):
        def attempt():
            HttpClient().delete('something')
        self.response.status_code = 500
        expect(attempt).to(raise_ex(HttpError))

    def test_covers_get(self):
        self.response.status_code = 500
        expect(send_get).to(raise_ex(HttpError))

    def test_covers_head(self):
        def attempt():
            HttpClient().head('something')
        self.response.status_code = 500
        expect(attempt).to(raise_ex(HttpError))

    def test_covers_options(self):
        def attempt():
            HttpClient().options('something')
        self.response.status_code = 500
        expect(attempt).to(raise_ex(HttpError))

    def test_covers_post(self):
        def attempt():
            HttpClient().post('something')
        self.response.status_code = 500
        expect(attempt).to(raise_ex(HttpError))

    def test_covers_put(self):
        def attempt():
            HttpClient().put('something')
        self.response.status_code = 500
        expect(attempt).to(raise_ex(HttpError))

    def test_redirect_on_3xx_lower(self):
        self.response.status_code = 300
        expect(send_get).to(raise_ex(error.HttpRedirect))

    def test_redirect_on_3xx_upper(self):
        self.response.status_code = 399
        expect(send_get).to(raise_ex(error.HttpRedirect))

    def test_bad_request_on_400(self):
        self.response.status_code = 400
        expect(send_get).to(raise_ex(error.HttpBadRequest))

    def test_unauthorized_on_401(self):
        self.response.status_code = 401
        expect(send_get).to(raise_ex(error.HttpUnauthorized))

    def test_payment_required_on_402(self):
        self.response.status_code = 402
        expect(send_get).to(raise_ex(error.HttpPaymentRequired))

    def test_forbidden_on_403(self):
        self.response.status_code = 403
        expect(send_get).to(raise_ex(error.HttpForbidden))

    def test_not_found_on_404(self):
        self.response.status_code = 404
        expect(send_get).to(raise_ex(error.HttpNotFound))

    def test_method_not_allowed_on_405(self):
        self.response.status_code = 405
        expect(send_get).to(raise_ex(error.HttpMethodNotAllowed))

    def test_not_acceptable_on_406(self):
        self.response.status_code = 406
        expect(send_get).to(raise_ex(error.HttpNotAcceptable))

    def test_proxy_authentication_required_on_407(self):
        self.response.status_code = 407
        expect(send_get).to(
            raise_ex(error.HttpProxyAuthenticationRequired))

    def test_request_timeout_on_408(self):
        self.response.status_code = 408
        expect(send_get).to(raise_ex(error.HttpRequestTimeout))

    def test_conflict_on_409(self):
        self.response.status_code = 409
        expect(send_get).to(raise_ex(error.HttpConflict))

    def test_gone_on_410(self):
        self.response.status_code = 410
        expect(send_get).to(raise_ex(error.HttpGone))

    def test_length_required_on_411(self):
        self.response.status_code = 411
        expect(send_get).to(raise_ex(error.HttpLengthRequired))

    def test_payload_too_large_on_413(self):
        self.response.status_code = 413
        expect(send_get).to(raise_ex(error.HttpPayloadTooLarge))

    def test_uri_too_long_on_414(self):
        self.response.status_code = 414
        expect(send_get).to(raise_ex(error.HttpUriTooLong))

    def test_unsupported_media_type_on_415(self):
        self.response.status_code = 415
        expect(send_get).to(raise_ex(error.HttpUnsupportedMediaType))

    def test_expectation_failed_on_417(self):
        self.response.status_code = 417
        expect(send_get).to(raise_ex(error.HttpExpectationFailed))

    def test_upgrade_required_on_426(self):
        self.response.status_code = 426
        expect(send_get).to(raise_ex(error.HttpUpgradeRequired))

    def test_client_error_on_upper_4xx(self):
        self.response.status_code = 499
        expect(send_get).to(raise_ex(error.HttpClientError))

    def test_internal_server_error_on_500(self):
        self.response.status_code = 500
        expect(send_get).to(raise_ex(error.HttpInternalServerError))

    def test_not_implemented_on_501(self):
        self.response.status_code = 501
        expect(send_get).to(raise_ex(error.HttpNotImplemented))

    def test_bad_gateway_on_502(self):
        self.response.status_code = 502
        expect(send_get).to(raise_ex(error.HttpBadGateway))

    def test_service_unavailable_on_503(self):
        self.response.status_code = 503
        expect(send_get).to(raise_ex(error.HttpServiceUnavailable))

    def test_gateway_timeout_on_504(self):
        self.response.status_code = 504
        expect(send_get).to(raise_ex(error.HttpGatewayTimeout))

    def test_http_version_not_supported_on_505(self):
        self.response.status_code = 505
        expect(send_get).to(
            raise_ex(error.HttpHttpVersionNotSupported))

    def test_http_server_error_on_upper_5xx(self):
        self.response.status_code = 599
        expect(send_get).to(raise_ex(error.HttpServerError))

    def test_none_on_lt_300(self):
        self.response.status_code = 299
        expect(send_get).not_to(raise_ex(error.HttpError))


if '__main__' == __name__:
    main()
