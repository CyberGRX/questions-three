import json
from unittest import TestCase, main

import requests
from expects import expect, equal
from parameterized import parameterized
from twin_sister import open_dependency_context, dependency_context
from twin_sister.expects_matchers import complain

from questions_three.graphql import OperationFailed
from twin_sister.fakes import EndlessFake


class TestOperationFailed(TestCase):

    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_logging=True)

    def tearDown(self):
        self.context.close()

    def test_requests_response_is_a_keyword_argument(self):
        try:
            OperationFailed(requests.Response())
        except TypeError as exception:
            expect(exception.args[0]).to(equal('Refusing to work until given a requests.Response object'))

    def test_requires_requests_response_object(self):
        def init_good_operation_failed():
            fake_requests_response = requests.Response()
            fake_requests_response.json = lambda: {'errors': 'who cares'}
            OperationFailed(requests_response=fake_requests_response)

        expect(init_good_operation_failed).to_not(complain(TypeError))

    def test_fails_to_init_without_requests_response_object(self):
        def init_bad_operation_failed():
            OperationFailed(requests_response='Thats no good')

        try:
            init_bad_operation_failed()
            assert False, 'Bad OperationFailed did not raise a TypeError'
        except TypeError as exception:
            expect(exception.args[0]).to(equal('Refusing to work until given a requests.Response object'))

    def test_response_is_saved_as_http_response_property(self):
        expected_response = requests.Response()
        expected_response.json = lambda: {'errors': 'who cares'}
        expected_url = 'this is a specific url'
        expected_response.url = expected_url
        sut = OperationFailed(requests_response=expected_response)

        assert sut.http_response == expected_response, 'Did not receive same expected_response object'

    @parameterized.expand([
        'this is what were looking for',
        'these are not the droids youre looking for'
    ])
    def test_operation_property(self, expected_operation):
        fake_requests_response = requests.Response()
        fake_requests_response.json = lambda: {'errors': 'who cares'}
        fake_requests_response.request = requests.PreparedRequest()
        fake_requests_response.request.body = json.dumps({'query': expected_operation})
        sut = OperationFailed(requests_response=fake_requests_response)

        expect(sut.operation).to(equal(expected_operation))

    @parameterized.expand([
        ({'vari': 1, 'able': 2},),
        ({'time': 1, 'step': 2},)
    ])
    def test_operation_variables_property(self, expected_variables):
        fake_requests_response = requests.Response()
        fake_requests_response.json = lambda: {'errors': 'who cares'}
        fake_requests_response.request = requests.PreparedRequest()
        fake_requests_response.request.body = json.dumps({'variables': expected_variables})
        sut = OperationFailed(requests_response=fake_requests_response)

        expect(sut.operation_variables).to(equal(expected_variables))

    @parameterized.expand([
        ({'expected': 'things'},),
        ({'expected': 'dings'},)
    ])
    def test_data_property(self, expected_data):
        fake_requests_response = requests.Response()
        fake_requests_response.json = lambda: {'data': expected_data, 'errors': 'who cares'}
        sut = OperationFailed(requests_response=fake_requests_response)

        expect(sut.data).to(equal(expected_data))

    @parameterized.expand([
        ([{'message': 'youre bad at requests'}],),
        ([{'message': 'heres a 400', 'locations': []}],)
    ])
    def test_errors_property(self, expected_errors):
        fake_requests_response = requests.Response()
        fake_requests_response.json = lambda: {'errors': expected_errors}
        sut = OperationFailed(requests_response=fake_requests_response)

        expect(sut.errors).to(equal(expected_errors))

    @parameterized.expand([
        'You wrote this test bad',
        'shaaaame, shame on you'
    ])
    def test_str_returns_when_error_messages_present(self, expected_message):
        fake_messages = [{'message': expected_message}]
        fake_requests_response = requests.Response()
        fake_requests_response.json = lambda: {'errors': fake_messages}
        expected_str_output = f"Operation Failed: ['{expected_message}']"
        sut = OperationFailed(requests_response=fake_requests_response)

        expect(str(sut)).to(equal(expected_str_output))

    @parameterized.expand([
        ([{'message': '', 'location': 'right here'}],),
        ([{'location': 'over there', 'extensions': [{'lets make this': 'complicated'}]}],)
    ])
    def test_str_returns_whole_error_json_if_does_not_include_messages(self, expected_output):
        fake_requests_response = requests.Response()
        fake_requests_response.json = lambda: {'errors': expected_output}
        sut = OperationFailed(requests_response=fake_requests_response)

        expect(str(sut)).to(equal(str(f'Operation Failed: {expected_output}')))

    @parameterized.expand([
        (('this is a custom message',),),
        (('this is the first message', 'this is the second message'),)
    ])
    def test_operation_failed_passes_args_to_super_correctly(self, expected_args):
        fake_requests_response = requests.Response()
        fake_requests_response.json = lambda: {'errors': 'who cares'}

        fake_init = EndlessFake()

        class FakeSupered:
            def __init__(*args, **kwargs):
                fake_init.inited_args = args
                fake_init.inited_kwargs = kwargs

        with dependency_context(supply_env=True, supply_logging=True) as temporary_context:
            temporary_context.inject(super, lambda *args: FakeSupered)

            OperationFailed(*expected_args, requests_response=fake_requests_response)

            for index, arg in enumerate(expected_args):
                expect(fake_init.inited_args[index]).to(equal(arg))


if __name__ == '__main__':
    main()
