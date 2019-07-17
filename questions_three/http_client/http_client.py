import requests
from twin_sister import dependency

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker, subscribe_event_handlers
from questions_three.exceptions import TooManyRedirects
from questions_three.logging import logger_for_module
from questions_three.module_cfg import config_for_module

from .construct_redirect_url import construct_redirect_url
from .extract_location_header import extract_location_header
from .inspect_response import inspect_response
from .transcript import Transcript

HTTP_METHODS = ('delete', 'get', 'head', 'options', 'patch', 'post', 'put')

# See https://tools.ietf.org/html/rfc7231#section-6.4.4
# and https://tools.ietf.org/html/rfc7238 for 308
HANDLE_THESE_REDIRECT_STATUS_CODES = (301, 302, 303, 307, 308)

STOP_FOLLOWING_REDIRECTS_AFTER_THIS_MANY = 5


class HttpClient:

    def __init__(self):
        subscribe_event_handlers(self)
        config = config_for_module(__name__)
        self._proxies = {}
        if config.http_proxy:
            self._proxies['http'] = config.http_proxy
        if config.https_proxy:
            self._proxies['https'] = config.https_proxy
        self._logger = logger_for_module(__name__)
        self._session = None
        self._persistent_headers = {}
        self._transcript = Transcript()
        self._verify_certs = config.https_verify_certs

    def enable_cookies(self):
        self._session = dependency(requests).Session()

    def set_persistent_headers(self, **kwargs):
        """
        Instruct the client to send the specified headers with each request

        Specify headers as keyword arguments (name1=val1, name2=val2...)
        """
        for k, v in kwargs.items():
            if v is None:
                if k in self._persistent_headers.keys():
                    del self._persistent_headers[k]
            else:
                self._persistent_headers[k] = v

    def on_suite_erred(self, suite_name=None, test_name=None, **kwargs):
        EventBroker.publish(
            event=TestEvent.artifact_created,
            artifact=str(self._transcript),
            artifact_mime_type='text/plain',
            artifact_type='http_transcript',
            suite_name=suite_name,
            test_name=test_name)

    on_test_erred = on_suite_erred
    on_test_failed = on_suite_erred

    def _send_plain_request(self, method, *args, **kwargs):
        kwargs['allow_redirects'] = False
        if self._proxies and 'proxies' not in kwargs.keys():
            kwargs['proxies'] = self._proxies
        func = getattr(dependency(requests), method)
        return func(*args, timeout=self._socket_timeout(), **kwargs)

    def _send_session_request(
            self, method, url, *, verify, proxies=None, **kwargs):
        request = requests.Request(method.upper(), url, **kwargs)
        prepped = self._session.prepare_request(request)
        return self._session.send(
            prepped, allow_redirects=False, verify=verify,
            proxies=proxies or self._proxies,
            timeout=self._socket_timeout())

    @staticmethod
    def _check_request_kwargs(kwargs):
        if 'json' in kwargs.keys():
            raise NotImplementedError(
                'I do not support "json" because I am a transport component. '
                'Consider specifying "data=json.dumps(thing)" instead.')

    def _socket_timeout(self):
        config = config_for_module(__name__)
        timeout = config.http_client_socket_timeout
        if timeout == '':
            timeout = None
        if timeout is not None:
            try:
                timeout = float(timeout)
            except ValueError as e:
                raise TypeError(
                    'expected $CLIENT_SOCKET_TIMEOUT '
                    f'("{timeout}") to be a number'
                    ) from e
        return timeout

    def _request(
            self, method, url, headers={},
            redirect_depth=0, **kwargs):
        self._check_request_kwargs(kwargs)
        headers = dict(self._persistent_headers, **headers)
        self._transcript.add_request(
            method, url, headers=headers, **kwargs)
        self._logger.debug('%s %s' % (method.upper(), url))
        if self._session is None:
            func = self._send_plain_request
        else:
            func = self._send_session_request
        resp = func(
            method, url, headers=headers, verify=self._verify_certs,
            **kwargs)
        self._logger.debug('HTTP %d\n%s' % (resp.status_code, resp.text))
        self._transcript.add_response(resp)
        if resp.status_code in HANDLE_THESE_REDIRECT_STATUS_CODES:
            if redirect_depth >= STOP_FOLLOWING_REDIRECTS_AFTER_THIS_MANY - 1:
                raise TooManyRedirects(
                    'Detected likely infinite HTTP redirection')
            return self._request(
                method,
                construct_redirect_url(
                    request_url=url,
                    response_location_header=extract_location_header(resp)),
                headers=headers, redirect_depth=redirect_depth+1, **kwargs)
        inspect_response(resp)
        return resp

    def _request_func(self, method):
        def f(*args, **kwargs):
            return self._request(method, *args, **kwargs)
        return f

    def __getattr__(self, name):
        if name in HTTP_METHODS:
            return self._request_func(name)
        raise AttributeError('I have no "%s"' % name)
