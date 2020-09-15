from unittest import TestCase, main

from expects import expect
from twin_sister.expects_matchers import contain_key_with_value
from twin_sister.fakes import EndlessFake, MasterSpy
from selenium import webdriver
from twin_sister import open_dependency_context

from questions_three_selenium.browser import Browser
from questions_three_selenium.browser_stack_tunnel import BrowserStackTunnel


class TestLocalId(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_fs=True)
        self.context.set_env(
            BROWSERSTACK_ACCESS_KEY="lomein",
            BROWSERSTACK_URL="spam",
            BROWSERSTACK_USERNAME="lilome",
            BROWSER_LOCATION="BrowserStack",
            BROWSERSTACK_SET_LOCAL="True",
        )
        self.fake_tunnel = EndlessFake()
        self.context.inject_as_class(BrowserStackTunnel, self.fake_tunnel)
        self.webdriver_spy = MasterSpy(EndlessFake())
        self.context.inject(webdriver, self.webdriver_spy)

    def extract_capabilities(self):
        spy = self.webdriver_spy.attribute_spies["Remote"]
        args, kwargs = spy.call_history[-1]
        return kwargs["desired_capabilities"]

    def test_sends_local_id_from_tunnel_to_webdriver(self):
        local_id = "McGill"
        self.fake_tunnel.local_identifier = local_id
        Browser()
        expect(self.extract_capabilities()).to(contain_key_with_value("browserstack.localIdentifier", local_id))


if "__main__" == __name__:
    main()
