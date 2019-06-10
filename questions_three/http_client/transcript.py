from datetime import datetime

from twin_sister import dependency


def expand_headers(headers):
    return '\n'.join(['%s: %s' % (k, v) for k, v in headers.items()])


def now():
    return dependency(datetime.utcnow)()


class Request:

    def __init__(self, method, url, headers={}, data=None, **kwargs):
        self.timestamp = now()
        self.method = method.upper()
        self.url = url
        self.headers = headers
        self.data = '\n\n' + str(data) if data else ''

    def __str__(self):
        return (
            ' --------- Request at %s\n' % self.timestamp.isoformat() +
            '%s %s\n' % (self.method, self.url) +
            expand_headers(self.headers) +
            self.data)


class Response:

    def __init__(self, requests_response):
        self.timestamp = now()
        self.response = requests_response

    def __str__(self):
        body = '\n\n%s' % self.response.text if self.response.text else ''
        return (
            ' --------- Response at %s\n' % self.timestamp.isoformat() +
            '\n%d\n' % self.response.status_code +
            expand_headers(self.response.headers) +
            body)


class Transcript:

    def __init__(self):
        self.records = []

    def add_request(self, method,  url, **kwargs):
        self.records.append(Request(method, url, **kwargs))

    def add_response(self, requests_response):
        self.records.append(Response(requests_response))

    def __str__(self):
        return '\n\n'.join([str(r) for r in self.records])
