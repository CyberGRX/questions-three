from unittest import TestCase, main

from expects import expect, equal
from selenium import webdriver
from twin_sister import open_dependency_context

from questions_three_selenium.browser import Browser


class FakeWebdriver:

    def __init__(self):
        self.script_executed = None

    def execute_script(self, script):
        self.script_executed = script

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        return self


class TestAddToLocalStorage(TestCase):

    def setUp(self):
        self.context = open_dependency_context(supply_env=True)

    def tearDown(self):
        self.context.close()

    def test_executes_expected_javascript(self):
        spy = FakeWebdriver()
        self.context.inject(webdriver, spy)
        key = 'my favorite things'
        value = 'candy when it rots, dirty smelly socks, and pot'
        Browser().add_to_local_storage(key=key, value=value)
        expect(spy.script_executed).to(
            equal("window.localStorage.setItem('%s', '%s');" % (key, value)))


if '__main__' == __name__:
    main()
