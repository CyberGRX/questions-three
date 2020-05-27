import requests
from uuid import uuid4

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

# See https://tools.ietf.org/html/rfc7231#section-6.4.4
# and https://tools.ietf.org/html/rfc7238 for 308
HANDLE_THESE_REDIRECT_STATUS_CODES = (301, 302, 303, 307, 308)

STOP_FOLLOWING_REDIRECTS_AFTER_THIS_MANY = 5


class HttpClient:

    def __init__(self):
        subscribe_event_handlers(self)
        config = config_for_module(__name__)
        log = logger_for_module(__name__)
        self._proxies = {}
        if config.http_proxy:
            proxy = config.http_proxy
            self._proxies['http'] = proxy
            log.debug(f'Using HTTP proxy {proxy}')
        if config.https_proxy:
            proxy = config.https_proxy
            self._proxies['https'] = proxy
            log.debug(f'(Using HTTPS proxy {proxy}')
        self._exception_callbacks = {}
        self._logger = logger_for_module(__name__)
        self._session = None
        self._persistent_headers = {}
        self._transcript = Transcript()
        self._verify_certs = config.https_verify_certs
        log.debug(f'Socket timeout: {self._socket_timeout()}')

    def enable_cookies(self):
        self._session = dependency(requests).Session()

    def set_exceptional_response_callback(self, *, exception_class, callback):
        """
        If the response contains an exceptional response code that
        maps to the given exception class, call the given function with
        the exception as the "exception" keyword argument.

        Limitation: You can't add a parent or child class of an exception
          that has already been added.
        """
        for existing in self._exception_callbacks.keys():
            if (
                    issubclass(existing, exception_class) or
                    issubclass(exception_class, existing)):
                raise TypeError(
                    f'Cannot add {exception_class.__name__} because related '
                    f'{existing.__name__} is already present')
        self._exception_callbacks[exception_class] = callback

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

    def delete(self, *args, **kwargs):
        return self._request('delete', *args, **kwargs)

    def get(self, *args, **kwargs):
        return self._request('get', *args, **kwargs)

    def head(self, *args, **kwargs):
        return self._request('head', *args, **kwargs)

    def options(self, *args, **kwargs):
        return self._request('options', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._request('patch', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._request('post', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._request('put', *args, **kwargs)

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
            self, method, url, headers={}, data=None,
            redirect_depth=0, **kwargs):
        self._check_request_kwargs(kwargs)
        headers = dict(self._persistent_headers, **headers)
        self._transcript.add_request(
            method, url, data=data, headers=headers, **kwargs)
        self._logger.debug('%s %s' % (method.upper(), url))
        self._logger.debug(f'Request headers: {headers}')
        if self._session is None:
            func = self._send_plain_request
        else:
            func = self._send_session_request
        request_uuid = uuid4()
        EventBroker.publish(
            event=TestEvent.http_request_sent,
            http_method=method.upper(),
            request_headers=headers, request_url=url,
            request_data=data, request_uuid=request_uuid)
        resp = func(
            method, url, headers=headers, data=data,
            verify=self._verify_certs, **kwargs)
        EventBroker.publish(
            event=TestEvent.http_response_received,
            request_uuid=request_uuid, response=resp)
        self._logger.debug('HTTP %d\n%s' % (resp.status_code, resp.text))
        self._logger.debug(f'Response headers: {resp.headers}')
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
                data=data, headers=headers, redirect_depth=redirect_depth + 1,
                **kwargs)
        try:
            dependency(inspect_response)(resp)
        except Exception as e:
            for exception_class, callback in self._exception_callbacks.items():
                if isinstance(e, exception_class):
                    response = callback(exception=e)
                    if response is not None:
                        return response
            raise

        return resp
