import json
from unittest import TestCase, main

import requests
from expects import expect, equal, have_keys, be_a
from parameterized import parameterized
from twin_sister.expects_matchers import complain

from questions_three.graphql import GraphqlClient, GraphqlResponse, OperationFailed
from twin_sister import open_dependency_context
from twin_sister.fakes import EndlessFake, FunctionSpy


class TestExecute(TestCase):

    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_logging=True)
        self.fake_http_client = EndlessFake()
        self.fake_requests_response = requests.Response()
        self.fake_requests_response.json = lambda: {}
        self.post_spy = FunctionSpy(return_value=self.fake_requests_response)
        self.fake_http_client.post = self.post_spy
        self.graph_client = GraphqlClient(http_client=self.fake_http_client, url='ignore me')

    def tearDown(self):
        self.context.close()

    def default_execute(self):
        return self.graph_client.execute('a not important operation', **{'dingle': 'dangle'})

    @parameterized.expand([
        'a real operation',
        'mutation is cool'
    ])
    def test_sends_operation_through_http_client(self, expected_operation):
        graph_client = GraphqlClient(http_client=self.fake_http_client, url='a real url')
        graph_client.execute(expected_operation)

        formatted_data = json.loads(self.post_spy.kwargs_from_last_call()['data'])
        expect(formatted_data).to(have_keys(query=expected_operation))

    @parameterized.expand([
        'send it here',
        'the correct url now'
    ])
    def test_sends_operation_to_correct_url_through_http_client(self, expected_url):
        graph_client = GraphqlClient(http_client=self.fake_http_client, url=expected_url)
        graph_client.execute('a not important operation')

        expect(self.post_spy.kwargs_from_last_call()).to(have_keys(url=expected_url))

    @parameterized.expand([
        ({'dingle': 'dangle'},),
        ({'dangle': ['dingle', 'dongle']},)
    ])
    def test_sends_kwargs_as_variables(self, expected_variables):
        self.graph_client.execute('a not important operation', **expected_variables)

        formatted_data = json.loads(self.post_spy.kwargs_from_last_call()['data'])
        expect(formatted_data).to(have_keys(variables=expected_variables))

    def test_sends_data_as_a_json_formatted_string(self):
        self.default_execute()

        data = self.post_spy.kwargs_from_last_call()['data']

        def json_loads():
            json.loads(data)

        expect(json_loads).to_not(complain(json.decoder.JSONDecodeError))

    def test_sends_content_type_application_json_header(self):
        self.default_execute()

        headers = self.post_spy.kwargs_from_last_call()['headers']

        expect(headers['Content-Type']).to(equal('application/json'))

    def test_returns_a_graph_ql_response_object(self):
        response = self.default_execute()

        expect(response).to(be_a(GraphqlResponse))

    def test_graph_ql_response_object_is_passed_response_from_operation(self):
        expected_url = 'a fake url'
        self.fake_requests_response.url = expected_url
        post_spy = FunctionSpy(return_value=self.fake_requests_response)
        self.fake_http_client.post = post_spy

        response = self.default_execute()

        assert response.http_response == self.fake_requests_response, f"Was not passed the fake_requests_response " \
                                                                      f"with url: '{expected_url}'"

    def test_raises_operation_failed_exception(self):
        self.fake_requests_response.json = lambda: {'errors': ['this did not go well']}

        expect(self.default_execute).to(complain(OperationFailed))

    def test_operation_failed_exception_is_passed_response_from_operation(self):
        self.fake_requests_response.json = lambda: {'errors': ['this did not go well']}
        expected_url = 'this is a unique identifier'
        self.fake_requests_response.url = expected_url

        try:
            self.default_execute()
            assert False, 'The operation did not fail'
        except OperationFailed as exception:
            assert exception.http_response == self.fake_requests_response, f"Was not passed the fake_requests_response " \
                                                                           f"with url: '{expected_url}'"

    def test_operation_does_not_catch_http_client_exceptions(self):
        def fake_post():
            raise fake_http_error

        fake_http_error = Exception()
        self.fake_http_client.post = lambda **kwargs: fake_post()

        try:
            self.default_execute()
            assert False, 'The exception was not raised'
        except Exception as actual:
            expect(actual).to(equal(fake_http_error))

    @parameterized.expand([
        ('str', 'this is a string with the word errors in it'),
        ('list', ['errors', 'this should not happen'])
    ])
    def test_execute_finds_errors_in_response_through_keys(self, object_type, bad_response):
        self.fake_requests_response.json = lambda: bad_response

        try:
            self.default_execute()
            assert False, 'Expected #execute to raise an an AttributeError'
        except AttributeError as error:
            expect(error.args[0]).to(equal(f"'{object_type}' object has no attribute 'keys'"))


if __name__ == '__main__':
    main()
