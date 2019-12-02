from unittest import TestCase, main
from time import sleep

from expects import expect, equal
from questions_three.http_client import HttpClient
from twin_sister.fakes import EndlessFake
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from twin_sister import TimeController, open_dependency_context

from questions_three_selenium.browser import Browser
from questions_three_selenium.browser_stack_tunnel import BrowserStackTunnel

# Actual error message from WebDriver
ERROR_MESSAGE = '[browserstack.local] is set to true but local testing ' \
    'through BrowserStack is not connected'


class FakeWebdriver:

    def __init__(self):
        self.init_exception = None

    def __call__(self, *args, **kwargs):
        if self.init_exception:
            raise self.init_exception
        return self

    def __getattr__(self, name):
        return self


class TestTunnelTimeout(TestCase):

    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_fs=True)
        self.context.inject(HttpClient, EndlessFake())
        self.context.inject_as_class(BrowserStackTunnel, EndlessFake())
        self.fake_webdriver = FakeWebdriver()
        self.context.inject(webdriver, self.fake_webdriver)
        self.context.set_env(
            BROWSER_LOCATION='BrowserStack',
            BROWSERSTACK_ACCESS_KEY='whatever',
            BROWSERSTACK_SET_LOCAL='true',
            BROWSERSTACK_URL='gopher:veronica',
            BROWSERSTACK_USERNAME='giggles')

    def tearDown(self):
        self.context.close()

    def test_waits_up_to_timeout(self):
        timeout = 1
        self.context.set_env(browserstack_tunnel_timeout=timeout)
        self.fake_webdriver.init_exception = WebDriverException(
            ERROR_MESSAGE)
        clock = TimeController(target=Browser, parent_context=self.context)
        clock.start()
        sleep(0.05)  # Give the SUT a chance to start
        clock.advance(seconds=timeout-0.01)
        sleep(0.05)  # Give the SUT a chance to cycle
        self.fake_webdriver.init_exception = None
        clock.join()
        expect(clock.exception_caught).to(equal(None))

    def test_expires_after_timeout(self):
        timeout = 1
        self.context.set_env(browserstack_tunnel_timeout=timeout)
        e = WebDriverException(ERROR_MESSAGE)
        self.fake_webdriver.init_exception = e
        clock = TimeController(target=Browser, parent_context=self.context)
        clock.start()
        sleep(0.05)  # Give the SUT a chance to start
        clock.advance(seconds=timeout + 0.01)
        clock.join()
        expect(clock.exception_caught).to(equal(e))


if '__main__' == __name__:
    main()
