from unittest import TestCase, main

from expects import expect, contain
from twin_sister.fakes import EndlessFake
from selenium import webdriver
from twin_sister import open_dependency_context

from questions_three_selenium.browser import Browser


class OptionsSpy:
    def __init__(self):
        self.arguments = []

    def add_argument(self, arg):
        self.arguments.append(arg)


class TestUserAgent(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True)
        self.context.inject(webdriver, EndlessFake())
        self.context.set_env(BROWSER_LOCATION="local", USE_BROWSER="Chrome")

    def tearDown(self):
        self.context.close()

    def test_sets_arbitrary_chrome_agent(self):
        expected = "agent-86;mozilla/jamf"
        self.context.set_env(CHROME_USER_AGENT=expected)
        options_spy = OptionsSpy()
        self.context.inject_as_class(webdriver.chrome.options.Options, options_spy)
        Browser()
        expect(options_spy.arguments).to(contain("user-agent=%s" % expected))


if "__main__" == __name__:
    main()
