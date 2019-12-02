from functools import partial
from unittest import TestCase, main

from expects import expect, equal
from twin_sister.expects_matchers import raise_ex
from twin_sister.fakes import EndlessFake
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from twin_sister import open_dependency_context

from questions_three_selenium.browser import Browser


class FakeElement:
    text = 'something'


class FakeWebDriver(EndlessFake):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.last_find_args = None
        self.matching_elements = [object()]

    def find_elements(self, *args):
        self.last_find_args = args
        return self.matching_elements

    def find_element_by_tag_name(self, name):
        return FakeElement()

    def __getattr__(self, name):
        return self

    def __call__(self, *args, **kwargs):
        return self


class TestFindAllMatchingElements(TestCase):

    def setUp(self):
        self.context = open_dependency_context(supply_env=True)
        self.fake_webdriver = FakeWebDriver()
        self.context.inject(webdriver, self.fake_webdriver)

    def tearDown(self):
        self.context.close()

    def test_transforms_qa_id_selector(self):
        Browser().find_all_matching_elements(qa_id='sausage')
        expect(self.fake_webdriver.last_find_args).to(
            equal((By.XPATH, "//*[@data-qa='sausage']")))

    def test_passes_other_selector_through_to_find_elements(self):
        tag_name = 'center'
        Browser().find_all_matching_elements(tag_name=tag_name)
        expect(self.fake_webdriver.last_find_args).to(
            equal((By.TAG_NAME, tag_name)))

    def test_returns_list_from_find_elements(self):
        thing1 = object()
        thing2 = object()
        expected = [thing1, thing2]
        self.fake_webdriver.matching_elements = expected
        expect(Browser().find_all_matching_elements(id='spam')).to(
            equal(expected))

    def test_raises_no_such_element_when_list_empty(self):
        self.fake_webdriver.matching_elements = []
        expect(partial(Browser().find_all_matching_elements, id='spam')).to(
            raise_ex(NoSuchElementException))


if '__main__' == __name__:
    main()
