"""
BrowserStack has a "Local" mode which creates a tunnel between the remote
browser and some non-public resource accessible to the host running tests.

https://www.browserstack.com/local-testing
"""

from unittest import TestCase, main

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from twin_sister.fakes import EndlessFake, MasterSpy
from selenium import webdriver
from twin_sister import open_dependency_context

from questions_three_selenium.browser import Browser
from questions_three_selenium.browser_stack_tunnel import BrowserStackTunnel


class TunnelToNowhere(BrowserStackTunnel):
    def __init__(self):
        super().__init__()
        self.was_closed = False

    def _open_new_tunnel(self):
        return

    def close(self):
        self.was_closed = True


class TestTunnel(TestCase):

    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_fs=True)
        self.context.inject(webdriver, EndlessFake())
        self.fake_tunnel_class = MasterSpy(EndlessFake())
        self.context.inject(
            BrowserStackTunnel, self.fake_tunnel_class)
        self.context.set_env(
            browserstack_access_key='whatever',
            browserstack_url='gopher:hahah',
            browserstack_username='biggles')

    def tearDown(self):
        self.context.close()

    def tunnel_was_opened(self):
        return bool(self.fake_tunnel_class.call_history)

    def test_opens_tunnel_on_suite_start_when_expected(self):
        self.context.set_env(
            browser_location='BrowserStack',
            browserstack_set_local='true')
        Browser()
        assert self.tunnel_was_opened(), 'Tunnel was not opened'

    def test_does_not_open_tunnel_if_not_using_browserstack(self):
        self.context.set_env(
            browser_location='Spain',
            browserstack_set_local='true')
        Browser()
        assert not self.tunnel_was_opened(), 'Tunnel was opened'

    def test_does_not_open_tunnel_if_local_flag_not_set(self):
        self.context.set_env(browser_locaton='BrowserStack')
        Browser()
        assert not self.tunnel_was_opened(), 'Tunnel was opened'

    def test_does_not_open_tunnel_if_local_flag_is_false(self):
        self.context.set_env(
            browser_locaton='BrowserStack',
            BROWSERSTACK_SET_LOCAL='fAlsE')
        Browser()
        assert not self.tunnel_was_opened(), 'Tunnel was opened'

    def test_closes_tunnel_on_suite_end(self):
        self.context.set_env(
            browser_locaton='BrowserStack',
            BROWSERSTACK_SET_LOCAL='true')
        spy = MasterSpy(TunnelToNowhere())
        self.context.inject_as_class(BrowserStackTunnel, spy)
        sut = Browser()  # noqa: F841
        assert not spy.was_closed,  'close was called prematurely.'
        EventBroker.publish(event=TestEvent.suite_ended)
        assert spy.was_closed, 'close was not called.'


if '__main__' == __name__:
    main()
