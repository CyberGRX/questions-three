import json

import requests
from twin_sister import dependency


class OperationFailed(RuntimeError):

    def errors_to_string(self):
        error_messages = list(filter(None, [error['message'] if 'message' in error else None for error in self.errors]))
        if error_messages == [''] or error_messages == []:
            return f'Operation Failed: {self.errors}'
        else:
            return f'Operation Failed: {error_messages}'

    def __init__(self, *args, requests_response=None):
        if not isinstance(requests_response, requests.Response):
            raise TypeError('Refusing to work until given a requests.Response object')
        self.http_response = requests_response
        all_args = args + (self.errors_to_string(),)
        dependency(super)().__init__(*all_args)

    def _request_body(self):
        return json.loads(self.http_response.request.body)

    @property
    def operation(self):
        return self._request_body()['query']

    @property
    def operation_variables(self):
        return self._request_body()['variables']

    def _response_json(self):
        return self.http_response.json()

    @property
    def data(self):
        return self._response_json()['data']

    @property
    def errors(self):
        return self._response_json()['errors']
