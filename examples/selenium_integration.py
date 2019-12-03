from expects import expect, contain
from questions_three.scaffolds.test_script import test, test_suite
from questions_three_selenium.browser.browser import Browser

with test_suite('SeleniumExample'):

    browser = Browser()
    browser.get('http://www.example.com')

    # This test will probably pass
    with test('Verify text contains example domain'):
        html = browser.find_unique_element(tag_name='html')
        expect(html.text.lower()).to(contain('example domain'))

    # This test should fail unless the Spinach Inquisition takes over example.com
    with test('Verify text contains Cardinal Biggles'):
        html = browser.find_unique_element(tag_name='html')
        expect(html.text.lower()).to(contain('Cardinal Biggles'))
