import json

from .operation_failed import OperationFailed
from .graphql_response import GraphqlResponse


class GraphqlClient:

    def __init__(self, *, http_client, url):
        self.http_client = http_client
        self.url = url

    def execute(self, operation, **variables):
        """
        :param operation: A string literal containing either a GraphQL query or mutation
        :param variables: Key=value pairs representing required variables for the GraphQL operation
        :return: A GraphQlResponse object on a successful request, an OperationFailed object when errors are detected in
        the response
        """
        response = self.http_client.post(
            url=self.url,
            headers={'Content-Type': 'application/json'},
            data=(json.dumps({'query': operation, 'variables': variables}))
        )
        if 'errors' in response.json().keys():
            raise OperationFailed(requests_response=response)
        return GraphqlResponse(response)
