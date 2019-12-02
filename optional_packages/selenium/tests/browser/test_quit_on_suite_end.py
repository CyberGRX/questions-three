from unittest import TestCase, main

from expects import expect, have_length
from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from twin_sister.fakes import EndlessFake, MasterSpy
from selenium import webdriver
from twin_sister import open_dependency_context

from questions_three_selenium.browser import Browser

USE_BROWSER = 'Chrome'


class TestQuitOnSuiteEnd(TestCase):

    def setUp(self):
        EventBroker.reset()
        self.context = open_dependency_context(supply_env=True)
        self.webdriver_spy = MasterSpy(EndlessFake())
        self.context.inject(webdriver, self.webdriver_spy)

    def tearDown(self):
        self.context.close()

    def quit_was_called(self):
        assert self.webdriver_spy.attribute_was_requested(USE_BROWSER), \
            '%s was not invoked' % USE_BROWSER
        launcher_spy = self.webdriver_spy.attribute_spies[USE_BROWSER]
        expect(launcher_spy.return_value_spies).to(have_length(1))
        driver_spy = launcher_spy.return_value_spies[0]
        if 'quit' in driver_spy.attribute_spies.keys():
            quit_spy = driver_spy.attribute_spies['quit']
            return bool(quit_spy.return_value_spies)
        return False

    def test_quits_browser_on_suite_end(self):
        sut = Browser()
        sut  # silence a warning about an unused variable
        assert not self.quit_was_called(), 'quit() was called prematurely'
        EventBroker.publish(event=TestEvent.suite_ended)
        assert self.quit_was_called(), 'quit() was not called'

    def set_debug_flag(self):
        self.context.set_env(SUPPRESS_BROWSER_EXIT_ON_FAILURE='tRuE')

    def test_does_not_quit_when_debugging_and_suite_erred(self):
        self.set_debug_flag()
        sut = Browser()
        sut
        EventBroker.publish(event=TestEvent.suite_erred)
        EventBroker.publish(event=TestEvent.suite_ended)
        assert not self.quit_was_called(), 'quit() was called'

    def test_does_not_quit_when_debugging_and_test_erred(self):
        self.set_debug_flag()
        sut = Browser()
        sut
        EventBroker.publish(event=TestEvent.test_erred)
        EventBroker.publish(event=TestEvent.suite_ended)
        assert not self.quit_was_called(), 'quit() was called'

    def test_does_not_quit_when_debugging_and_test_failed(self):
        self.set_debug_flag()
        sut = Browser()
        sut
        EventBroker.publish(event=TestEvent.test_failed)
        EventBroker.publish(event=TestEvent.suite_ended)
        assert not self.quit_was_called(), 'quit() was called'

    def test_quits_when_debugging_and_nothing_failed(self):
        self.set_debug_flag()
        sut = Browser()
        sut
        EventBroker.publish(event=TestEvent.suite_ended)
        assert self.quit_was_called(), 'quit() was not called'


if '__main__' == __name__:
    main()
