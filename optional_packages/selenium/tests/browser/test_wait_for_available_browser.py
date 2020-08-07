from time import sleep
from unittest import TestCase, main

from expects import expect, equal
from twin_sister.expects_matchers import complain
from twin_sister.fakes import EndlessFake
from questions_three.vanilla import func_that_raises
from selenium import webdriver
from twin_sister import TimeController, open_dependency_context

from questions_three_selenium.exceptions import AllBrowsersBusy
from questions_three_selenium.browser import Browser


class FakeException(RuntimeError):
    pass


class TestWaitForAvailableBrowser(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True)
        self.timeout = 1
        self.context.set_env(
            BROWSERSTACK_ACCESS_KEY="whatever",
            BROWSERSTACK_URL="http://whatever",
            BROWSERSTACK_USERNAME="whatever",
            BROWSER_LOCATION="browserstack",
            BROWSER_AVAILABILITY_TIMEOUT=self.timeout,
            BROWSER_AVAILABILITY_THROTTLE=0,
        )
        self.webdriver = EndlessFake()
        self.context.inject(webdriver, self.webdriver)

    def tearDown(self):
        self.context.close()

    def test_does_not_wait_after_other_exception(self):
        self.webdriver.Remote = func_that_raises(FakeException())
        expect(Browser).to(complain(FakeException))

    def test_waits_up_to_configured_limit(self):
        self.webdriver.Remote = func_that_raises(AllBrowsersBusy())
        ctl = TimeController(target=Browser, parent_context=self.context)
        ctl.start()
        sleep(0.05)
        ctl.advance(seconds=self.timeout - 0.01)
        sleep(0.05)
        try:
            expect(ctl.exception_caught).to(equal(None))
        finally:
            ctl.advance(days=180)
            ctl.join()

    def test_re_raises_after_timeout(self):
        raised = AllBrowsersBusy()
        self.webdriver.Remote = func_that_raises(raised)
        ctl = TimeController(target=Browser, parent_context=self.context)
        ctl.start()
        sleep(0.05)
        ctl.advance(seconds=self.timeout + 0.01)
        sleep(0.05)
        try:
            expect(ctl.exception_caught).to(equal(raised))
        finally:
            ctl.advance(days=180)
            ctl.join()


if "__main__" == __name__:
    main()
