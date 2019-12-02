from unittest import TestCase, main
from urllib.parse import quote_plus, urlsplit, urlunsplit

from expects import expect, contain, equal, raise_error
from twin_sister.expects_matchers import contain_key_with_value, raise_ex
from twin_sister.fakes import EndlessFake, MasterSpy
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from twin_sister import open_dependency_context

from questions_three.exceptions import InvalidConfiguration
from questions_three_selenium.browser import Browser
from questions_three_selenium.exceptions import AllBrowsersBusy


class TestLaunchBrowserStack(TestCase):

    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_fs=True)
        self.context.set_env(
            BROWSER_AVAILABILITY_TIMEOUT=0,
            BROWSER_AVAILABILITY_THROTTLE=0,
            BROWSERSTACK_URL='https://browserstack.not:43/really',
            BROWSERSTACK_OS='CP/M',
            BROWSERSTACK_OS_VERSION='1.7',
            USE_BROWSER='NCSA-Mosaic',
            USE_BROWSER_VERSION='1.3',
            BROWSERSTACK_SCREEN_RESOLUTION='kumquat',
            BROWSER_AVALABILITY_TIMEOUT='0',
            BROWSERSTACK_SET_LOCAL='fAlSe',
            BROWSERSTACK_SET_DEBUG='TrUe',
            BROWSER_LOCATION='BrowserStack',
            BROWSERSTACK_USERNAME='shady_sam@shady.shade',
            BROWSERSTACK_ACCESS_KEY='gdf0i9/38md-p00')
        self.webdriver_spy = MasterSpy(EndlessFake())
        self.context.inject(webdriver, self.webdriver_spy)

    def tearDown(self):
        self.context.close()

    def test_complains_if_environment_lacks_username(self):
        self.context.unset_env('BROWSERSTACK_USERNAME')
        expect(Browser).to(raise_error(InvalidConfiguration))

    def test_complains_if_environment_lacks_access_key(self):
        self.context.unset_env('BROWSERSTACK_ACCESS_KEY')
        expect(Browser).to(raise_error(InvalidConfiguration))

    def parse_command_executor(self):
        args, kwargs = self.webdriver_spy.last_call_to('Remote')
        expect(kwargs.keys()).to(contain('command_executor'))
        return urlsplit(kwargs['command_executor'])

    def retrieve_desired_capabilities(self):
        args, kwargs = self.webdriver_spy.last_call_to('Remote')
        expect(kwargs.keys()).to(contain('desired_capabilities'))
        return kwargs['desired_capabilities']

    def test_uses_configured_browserstack_url(self):
        expected = 'https://a.b.c/1'
        self.context.set_env(BROWSERSTACK_URL=expected)
        Browser()
        parsed = self.parse_command_executor()
        scheme, netloc, path, query, fragment = tuple(parsed)
        without_credentials = netloc.split('@')[-1]
        actual = urlunsplit(
            (scheme, without_credentials, path, query, fragment))
        expect(actual).to(equal(expected))

    def test_uses_urlencoded_configured_username(self):
        expected = 's.mcspamface@spamhaus.org'
        self.context.set_env(BROWSERSTACK_USERNAME=expected)
        Browser()
        parsed = self.parse_command_executor()
        expect(parsed.username).to(equal(quote_plus(expected)))

    def test_uses_urlencoded_configured_access_key(self):
        expected = 'PleaseOhPlease'
        self.context.set_env(BROWSERSTACK_ACCESS_KEY=expected)
        Browser()
        parsed = self.parse_command_executor()
        expect(parsed.password).to(equal(expected))

    def test_uses_configured_os(self):
        expected = 'OS/irus'
        self.context.set_env(BROWSERSTACK_OS=expected)
        Browser()
        expect(self.retrieve_desired_capabilities()).to(
            contain_key_with_value('os', expected))

    def test_uses_configured_os_version(self):
        expected = '14.7.1'
        self.context.set_env(BROWSERSTACK_OS_VERSION=expected)
        Browser()
        expect(self.retrieve_desired_capabilities()).to(
            contain_key_with_value('os_version', expected))

    def test_uses_configured_screen_resolution(self):
        expected = '8x10'
        self.context.set_env(BROWSERSTACK_SCREEN_RESOLUTION=expected)
        Browser()
        expect(self.retrieve_desired_capabilities()).to(
            contain_key_with_value('resolution', expected))

    def test_uses_configured_browser_type(self):
        expected = 'smoking'
        self.context.set_env(USE_BROWSER=expected)
        Browser()
        expect(self.retrieve_desired_capabilities()).to(
            contain_key_with_value('browser', expected))

    def test_uses_configured_browser_version(self):
        expected = 'nineteen'
        self.context.set_env(USE_BROWSER_VERSION=expected)
        Browser()
        expect(self.retrieve_desired_capabilities()).to(
            contain_key_with_value('browser_version', expected))

    def test_does_not_specify_browser_version_if_not_configured(self):
        self.context.unset_env('USE_BROWSER_VERSION')
        Browser()
        expect(self.retrieve_desired_capabilities().keys()).not_to(
            contain('browser_version'))

    def test_uses_configured_browserstack_local(self):
        expected = False
        self.context.set_env(BROWSERSTACK_SET_LOCAL=expected)
        Browser()
        expect(self.retrieve_desired_capabilities()).to(
            contain_key_with_value('browserstack.local', expected))

    def test_uses_configured_browserstack_debug(self):
        expected = True
        Browser()
        self.context.set_env(BROWSERSTACK_SET_DEBUG=expected)
        expect(self.retrieve_desired_capabilities()).to(
            contain_key_with_value('browserstack.debug', expected))

    def test_sets_full_screen(self):
        remote_spy = MasterSpy(EndlessFake())
        self.webdriver_spy.Remote = lambda *a, **k: remote_spy
        Browser()
        expect(remote_spy.attribute_spies.keys()).to(
            contain('fullscreen_window'))
        calls = remote_spy.attribute_spies['fullscreen_window'].call_history
        assert calls, 'fullscreen_window was not called'

    def test_detects_busy_signal(self):
        def busy(*args, **kwargs):
            raise WebDriverException(
                'All parallel tests are currently in use, '
                'including the queued tests. Please wait to '
                'finish or upgrade your plan to add more sessions.')
        self.webdriver_spy.Remote = busy
        expect(Browser).to(raise_ex(AllBrowsersBusy))


if '__main__' == __name__:
    main()
