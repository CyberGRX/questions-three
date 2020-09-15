from functools import partial
from unittest import TestCase, main

from expects import expect, be_false, be_true, equal
from twin_sister.expects_matchers import raise_ex
from twin_sister.fakes import EndlessFake
from selenium import webdriver
from selenium.webdriver.common.by import By
from twin_sister import open_dependency_context

from questions_three_selenium.browser import Browser
from questions_three_selenium.exceptions import UnknownSelector


class FakeElement:
    text = "something"


class FakeWebDriver(EndlessFake):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.last_find = None

    def find_element_by_tag_name(self, name):
        return FakeElement()

    def find_elements(self, by, selector):
        self.last_find = by, selector
        return self.elements

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        return self


class TestDoesElementExist(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True)
        self.fake_web_driver = FakeWebDriver()
        self.context.inject(webdriver, self.fake_web_driver)
        self.sut = Browser()

    def tearDown(self):
        self.context.close()

    def test_returns_true_if_element_exists(self):
        fake_element = object()
        self.fake_web_driver.elements = [fake_element]

        response = self.sut.element_exists(id="something")

        expect(response).to(be_true)

    def test_returns_false_if_no_such_element(self):
        response = self.sut.element_exists(id="something")

        expect(response).to(be_false)

    def test_can_identify_by_css_selector(self):
        self.fake_web_driver.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(css_selector=selector)
        expect(self.fake_web_driver.last_find).to(equal((By.CSS_SELECTOR, selector)))

    def test_can_identify_by_id(self):
        self.fake_web_driver.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(id=selector)
        expect(self.fake_web_driver.last_find).to(equal((By.ID, selector)))

    def test_can_identify_by_qa_id(self):
        self.fake_web_driver.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(qa_id=selector)
        expect(self.fake_web_driver.last_find).to(equal((By.XPATH, "//*[@data-qa='%s']" % selector)))

    def test_can_identify_by_link_text(self):
        self.fake_web_driver.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(link_text=selector)
        expect(self.fake_web_driver.last_find).to(equal((By.LINK_TEXT, selector)))

    def test_can_identify_by_tag_name(self):
        self.fake_web_driver.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(css_selector=selector)
        expect(self.fake_web_driver.last_find).to(equal((By.CSS_SELECTOR, selector)))

    def test_can_identify_by_name(self):
        self.fake_web_driver.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(name=selector)
        expect(self.fake_web_driver.last_find).to(equal((By.NAME, selector)))

    def test_can_identify_by_partial_link_text(self):
        self.fake_web_driver.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(partial_link_text=selector)
        expect(self.fake_web_driver.last_find).to(equal((By.PARTIAL_LINK_TEXT, selector)))

    def test_can_identify_by_xpath(self):
        self.fake_web_driver.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(xpath=selector)
        expect(self.fake_web_driver.last_find).to(equal((By.XPATH, selector)))

    def test_raises_unknown_selector(self):
        attempt = partial(self.sut.element_exists, spam="something")

        expect(attempt).to(raise_ex(UnknownSelector))


if __name__ == "__main__":
    main()
