import requests

from questions_three.vanilla import Structure


class GraphqlResponse:

    def __init__(self, requests_response):
        if not isinstance(requests_response, requests.Response):
            raise TypeError('Refusing to work until given a requests.Response')
        self.http_response = requests_response

    @property
    def data(self):
        return self.http_response.json()

    @property
    def data_as_structure(self):
        return Structure(**self.data)
