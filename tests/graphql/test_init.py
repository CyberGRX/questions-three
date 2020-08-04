from unittest import TestCase, main

from expects import expect, equal
from parameterized import parameterized
from questions_three.graphql import GraphqlClient
from questions_three.http_client import HttpClient
from twin_sister import open_dependency_context
from twin_sister.fakes import EndlessFake


class TestInit(TestCase):

    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_logging=True)

    def tearDown(self):
        self.context.close()

    def test_initializes_client_with_given_http_client(self):
        expected_http_client = HttpClient()
        graph_client = GraphqlClient(http_client=expected_http_client, url='not important')

        expect(graph_client.http_client).to(equal(expected_http_client))

    @parameterized.expand([
        'https://its.aaa/graph',
        'https://still.aaa/graph'
    ])
    def test_initializes_client_with_given_url(self, url):
        expected_url = url
        graph_client = GraphqlClient(http_client=EndlessFake(), url=expected_url)

        expect(graph_client.url).to(equal(expected_url))


if __name__ == '__main__':
    main()
