from unittest import TestCase, main

from expects import expect, be_a, contain, equal, have_length, raise_error
from twin_sister.fakes import EndlessFake, MasterSpy
from selenium import webdriver
from twin_sister import open_dependency_context

from questions_three_selenium.browser import Browser
from questions_three_selenium.exceptions import UnsupportedBrowser


class FakeWebdriver:

    def __init__(self):
        self.driver_used = None
        self.driver_spy = None

    def __getattr__(self, name):
        self.driver_used = name
        spy = MasterSpy(EndlessFake())
        self.driver_spy = spy
        return spy


class TestLaunchLocal(TestCase):

    def setUp(self):
        self.context = open_dependency_context(supply_env=True)
        self.fake_webdriver = FakeWebdriver()
        self.context.inject(webdriver, self.fake_webdriver)

    def tearDown(self):
        self.context.close()

    def test_complains_if_unknown_browser_requested(self):
        self.context.set_env(USE_BROWSER='mosaic')
        expect(Browser).to(raise_error(UnsupportedBrowser))

    def test_launches_chrome_if_specified(self):
        self.context.set_env(USE_BROWSER='cHrOmE')
        Browser()
        expect(self.fake_webdriver.driver_used).to(equal('Chrome'))

    def test_launches_firefox_if_specified(self):
        self.context.set_env(USE_BROWSER='FiReFoX')
        Browser()
        expect(self.fake_webdriver.driver_used).to(equal('Firefox'))

    def test_assumes_chrome_if_no_browser_specified(self):
        Browser()
        expect(self.fake_webdriver.driver_used).to(equal('Chrome'))

    def test_specifies_fullscreen_option(self):
        Browser()
        spy = self.fake_webdriver.driver_spy
        expect(spy).not_to(equal(None))
        expect(spy.call_history).to(have_length(1))
        _, kwargs = spy.call_history[0]
        expect(kwargs.keys()).to(contain('chrome_options'))
        opts = kwargs['chrome_options']
        expect(opts).to(be_a(webdriver.chrome.options.Options))
        expect(opts.arguments).to(contain('start-fullscreen'))


if '__main__' == __name__:
    main()
