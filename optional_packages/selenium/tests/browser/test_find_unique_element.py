from unittest import TestCase, main

from expects import expect, equal, raise_error
from twin_sister.fakes import EndlessFake
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from twin_sister import TimeController, open_dependency_context

from questions_three_selenium.browser import Browser
from questions_three_selenium.exceptions import TooManyElements, UnknownSelector


class FakeElement:

    text = "some fake content"


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


class TestFindUniqueElement(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True)
        self.fake = FakeWebDriver()
        self.context.inject(webdriver, self.fake)
        self.sut = Browser()

    def tearDown(self):
        self.context.close()

    def test_returns_element_if_only_one_present(self):
        element = object()
        self.fake.elements = [element]
        expect(self.sut.find_unique_element(id="whatever")).to(equal(element))

    def test_raises_no_such_element_if_none_present(self):
        def attempt():
            self.sut.find_unique_element(id="whatever", timeout=0)

        expect(attempt).to(raise_error(NoSuchElementException))

    def test_waits_up_to_timeout_for_element_to_appear(self):
        timeout = 42

        def find():
            return self.sut.find_unique_element(id="whatever", timeout=timeout)

        clock = TimeController(target=find)
        clock.start()
        clock.advance(seconds=timeout - 0.001)
        element = object()
        self.fake.elements = [element]
        clock.join()
        expect(clock.exception_caught).to(equal(None))
        expect(clock.value_returned).to(equal(element))

    def test_raises_too_many_elements_if_two_present(self):
        self.fake.elements = [object(), object()]

        def attempt():
            self.sut.find_unique_element(id="whatever")

        expect(attempt).to(raise_error(TooManyElements))

    def test_can_identify_by_class_name(self):
        self.fake.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(class_name=selector)
        expect(self.fake.last_find).to(equal((By.CLASS_NAME, selector)))

    def test_can_identify_by_css_selector(self):
        self.fake.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(css_selector=selector)
        expect(self.fake.last_find).to(equal((By.CSS_SELECTOR, selector)))

    def test_can_identify_by_id(self):
        self.fake.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(id=selector)
        expect(self.fake.last_find).to(equal((By.ID, selector)))

    def test_can_identify_by_qa_id(self):
        self.fake.elements = [object()]
        selector = "fake-qa-id"
        self.sut.find_unique_element(qa_id=selector)
        expect(self.fake.last_find).to(equal((By.XPATH, "//*[@data-qa='%s']" % selector)))

    def test_can_identify_by_link_text(self):
        self.fake.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(link_text=selector)
        expect(self.fake.last_find).to(equal((By.LINK_TEXT, selector)))

    def test_can_identify_by_tag_name(self):
        self.fake.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(tag_name=selector)
        expect(self.fake.last_find).to(equal((By.TAG_NAME, selector)))

    def test_can_identify_by_name(self):
        self.fake.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(name=selector)
        expect(self.fake.last_find).to(equal((By.NAME, selector)))

    def test_can_identify_by_partial_link_text(self):
        self.fake.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(partial_link_text=selector)
        expect(self.fake.last_find).to(equal((By.PARTIAL_LINK_TEXT, selector)))

    def test_can_identify_by_xpath(self):
        self.fake.elements = [object()]
        selector = "whatever"
        self.sut.find_unique_element(xpath=selector)
        expect(self.fake.last_find).to(equal((By.XPATH, selector)))

    def test_raises_unknown_selector(self):
        def attempt():
            self.sut.find_unique_element(robins=2)

        expect(attempt).to(raise_error(UnknownSelector))


if "__main__" == __name__:
    main()
