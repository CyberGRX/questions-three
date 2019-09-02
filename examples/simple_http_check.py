from expects import expect, contain, equal
from questions_three.http_client import HttpClient
from questions_three.scaffolds.check_script import check, check_suite


with check_suite('SimpleHttpCheck'):

    response = HttpClient().get('http://example.com/')

    with check('Verify status code is 200'):
        expect(response.status_code).to(equal(200))

    with check('Verify response contains expected text'):
        expect(response.text).to(contain('illustrative examples'))
