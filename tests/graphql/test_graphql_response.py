from unittest import TestCase, main

import requests
from expects import expect, equal, be_a
from parameterized import parameterized
from twin_sister import open_dependency_context
from twin_sister.expects_matchers import complain

from questions_three.graphql import GraphqlResponse
from questions_three.vanilla import Structure


class TestGraphqlResponse(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_logging=True)

    def tearDown(self):
        self.context.close()

    def test_requires_requests_object_not_empty(self):
        def init_empty_graph_ql_response():
            GraphqlResponse()

        expect(init_empty_graph_ql_response).to(complain(TypeError))

    def test_requires_request_object_not_other_input(self):
        def init_bad_graph_ql_response():
            GraphqlResponse("this is bad")

        try:
            init_bad_graph_ql_response()
            assert False, "Bad GraphQlResponse did not raise a TypeError"
        except TypeError as e:
            expect(e.args[0]).to(equal("Refusing to work until given a requests.Response"))

    def test_response_is_saved_as_http_response_property(self):
        expected_response = requests.Response()
        expected_url = "this is a url"
        expected_response.url = expected_url
        sut = GraphqlResponse(expected_response)

        assert sut.http_response == expected_response, "Did not receive same expected_response object"
        expect(sut.http_response.url).to(equal(expected_url))

    @parameterized.expand([({"things": "stuff"},), ({"stuff": "things"},)])
    def test_data_property(self, expected_dict):
        fake_requests_response = requests.Response()
        fake_requests_response.json = lambda: expected_dict
        sut = GraphqlResponse(fake_requests_response)

        expect(sut.data).to(be_a(dict))
        expect(sut.data).to(equal(expected_dict))

    @parameterized.expand([({"things": "stuff"},), ({"stuff": "things"},)])
    def test_data_as_structure_property(self, fake_json):
        expected_structure = Structure(**fake_json)
        fake_requests_response = requests.Response()
        fake_requests_response.json = lambda: fake_json
        sut = GraphqlResponse(fake_requests_response)

        expect(sut.data_as_structure).to(be_a(Structure))
        expect(sut.data_as_structure).to(equal(expected_structure))


if __name__ == "__main__":
    main()
