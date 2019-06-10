from functools import partial
from unittest import TestCase, main

from expects import expect
import requests
from twin_sister import open_dependency_context

from twin_sister.expects_matchers import raise_ex
from questions_three.http_client import HttpClient
from twin_sister.fakes import EmptyFake


class TestRejectsJsonArgument(TestCase):
    """
    Requests allows a "json" keyword argument to specify a dict or list
      to be converted to a json string and placed in the request payload.
    This feature mixes the encoding concern into a transport component and
      interefers with our transcript mechanism.
    """

    def setUp(self):
        self.context = open_dependency_context()
        self.context.inject(requests, EmptyFake())

    def tearDown(self):
        self.context.close()

    def test_raises_not_implemented(self):
        expect(partial(HttpClient().post, 'http://spam', json={'spam': 1})).to(
            raise_ex(NotImplementedError))


if '__main__' == __name__:
    main()
