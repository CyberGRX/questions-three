from unittest import TestCase, main

from expects import expect, contain, equal
from questions_three.exceptions import InvalidConfiguration
from selenium import webdriver
from twin_sister import open_dependency_context
from twin_sister.expects_matchers import complain
from twin_sister.fakes import EndlessFake, FunctionSpy

from questions_three_selenium.browser import Browser


class TestSeleniumGrid(TestCase):

    def setUp(self):
        self.context = open_dependency_context(
            supply_env=True, supply_logging=True)
        self.webdriver_stub = EndlessFake(pattern_obj=webdriver)
        self.remote_spy = FunctionSpy()
        self.webdriver_stub.Remote = self.remote_spy
        self.context.inject(webdriver, self.webdriver_stub)

    def tearDown(self):
        self.context.close()

    def test_sets_command_executor_to_selenium_grid_hub_url(self):
        hub_url = 'https://not-actually-a.grid:4200/hub'
        self.context.set_env(
            browser_location='selenium_grid', selenium_grid_hub_url=hub_url)
        Browser()
        expect(self.remote_spy['command_executor']).to(
            equal(hub_url))

    def test_complains_if_hub_url_not_specified(self):
        self.context.set_env(browser_location='selenium_grid')
        expect(Browser).to(complain(InvalidConfiguration))

    def test_sets_specified_browser_name(self):
        browser_name = 'Yogurt'
        self.context.set_env(
            BROWSER_LOCATION='selenium_grid',
            SELENIUM_GRID_HUB_URL='something', USE_BROWSER=browser_name)
        Browser()
        requested_capabilities = self.remote_spy['desired_capabilities']
        expect(requested_capabilities['browserName']).to(
            equal(browser_name))

    def test_sets_browser_version_if_specified(self):
        version = '8.67.5309'
        self.context.set_env(
            BROWSER_LOCATION='selenium_grid',
            SELENIUM_GRID_HUB_URL='fish',
            USE_BROWSER_VERSION=version)
        Browser()
        requested_capabilities = self.remote_spy['desired_capabilities']
        expect(requested_capabilities['version']).to(equal(version))

    def test_does_not_set_browser_version_if_not_specified(self):
        self.context.set_env(
            BROWSER_LOCATION='selenium_grid',
            SELENIUM_GRID_HUB_URL='http://biggles')
        Browser()
        caps = self.remote_spy['desired_capabilities']
        expect(caps.keys()).not_to(contain('version'))

    def test_returns_a_browser_with_the_remote_driver(self):
        get_spy = FunctionSpy(return_value=EndlessFake())
        remote_stub = EndlessFake()
        remote_stub.get = get_spy
        self.webdriver_stub.Remote = lambda *args, **kwargs: remote_stub
        self.context.set_env(
            BROWSER_LOCATION='selenium_grid',
            SELENIUM_GRID_HUB_URL='http://fang')
        Browser().get('http://stuffed')


if '__main__' == __name__:
    main()
