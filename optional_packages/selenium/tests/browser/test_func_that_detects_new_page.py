from unittest import TestCase, main

from twin_sister import open_dependency_context

from questions_three_selenium.browser import Browser
from questions_three_selenium.browser.launch_browser import launch_browser


class StubWebdriver:
    def __init__(self):
        self.html_elements = []

    def find_elements_by_tag_name(self, tag_name):
        if "html" == tag_name:
            return self.html_elements
        return []


class TestFuncThatDetectsNewPage(TestCase):
    def setUp(self):
        self.context = open_dependency_context()
        self.stub_webdriver = StubWebdriver()
        self.context.inject(launch_browser, lambda: self.stub_webdriver)

    def tearDown(self):
        self.context.close()

    def test_func_returns_false_when_nothing_has_changed(self):
        html_elements = [object()]
        sut = Browser()
        self.stub_webdriver.html_elements = [html_elements]
        change_detected = sut.func_that_detects_new_page()
        assert not change_detected(), "Detected a non-existent change"

    def test_func_returns_true_after_html_change(self):
        old_htmls = [object()]
        new_htmls = [object()]
        sut = Browser()
        self.stub_webdriver.html_elements = old_htmls
        change_detected = sut.func_that_detects_new_page()
        self.stub_webdriver.html_elements = new_htmls
        assert change_detected(), "Failed to detect a change"


if "__main__" == __name__:
    main()
