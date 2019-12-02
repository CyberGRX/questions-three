from datetime import datetime, timedelta

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker, subscribe_event_handlers
from questions_three.logging import logger_for_module
from questions_three.module_cfg import config_for_module
from questions_three.vanilla import random_base36_string
from questions_three_selenium.dom_dumper.dump_dom import dump_dom
from selenium.common.exceptions import NoSuchElementException
from twin_sister import dependency

from questions_three_selenium.exceptions import TooManyElements

from .launch_browser import launch_browser
from .kwargs2selector import kwargs2selector


def current_time():
    return dependency(datetime).now()


class Browser:

    def __init__(self):
        self._log = dependency(logger_for_module)(__name__)
        config = config_for_module(__name__)
        self.element_find_timeout = config.browser_element_find_timeout
        self.page_load_timeout = config.browser_page_load_timeout
        self._driver = dependency(launch_browser)()
        self._failure_detected = False
        subscribe_event_handlers(self)

    def add_to_local_storage(self, *, key, value):
        """
        Add an item to HTML 5 local storage
        """
        self._driver.execute_script(
            "window.localStorage.setItem('%s', '%s');" % (key, value))

    def find_all_matching_elements(self, **kwargs):
        elements = self._driver.find_elements(*kwargs2selector(**kwargs))
        if not elements:
            raise NoSuchElementException('Nothing matched %s' % kwargs)
        return elements

    def find_unique_element(
            self, *, timeout=None, **kwargs):
        if timeout is None:
            timeout = self.element_find_timeout
        expiry = current_time() + timedelta(seconds=timeout)
        while True:
            elements = self._driver.find_elements(*kwargs2selector(**kwargs))
            count = len(elements)
            if 1 > count and current_time() >= expiry:
                raise NoSuchElementException(kwargs)
            elif 1 == count:
                return elements[0]
            elif 1 < count:
                raise TooManyElements(
                    'Found %d elements matching %s' % (count, kwargs))

    def on_suite_erred(self, **kwargs):
        self._failure_detected = True
        # Take a screenshot only if we have open windows.
        if self._driver.window_handles:
            artifact_group = random_base36_string(3)
            self.publish_screenshot(artifact_group=artifact_group, **kwargs)
            self.publish_dom_dump(artifact_group=artifact_group, **kwargs)

    on_test_erred = on_suite_erred

    on_test_failed = on_suite_erred

    def on_suite_ended(self, **kwargs):
        config = config_for_module(__name__)
        if not (
                self._failure_detected and
                config.suppress_browser_exit_on_failure):
            self._driver.quit()

    def publish_dom_dump(
            self, artifact_group=None, suite_name=None, test_name=None,
            **kwargs):
        EventBroker.publish(
            artifact_group=artifact_group,
            event=TestEvent.artifact_created,
            artifact=dependency(dump_dom)(self),
            artifact_mime_type='text/html',
            artifact_type='dom_dump',
            suite_name=suite_name,
            test_name=test_name)

    def publish_screenshot(
            self, artifact_group=None, suite_name=None, test_name=None,
            **kwargs):
        EventBroker.publish(
            artifact_group=artifact_group,
            event=TestEvent.artifact_created,
            suite_name=suite_name,
            test_name=test_name,
            artifact=self._driver.get_screenshot_as_png(),
            artifact_type='screenshot',
            artifact_mime_type='image/png')

    def top_html_element(self):
        htmls = self._driver.find_elements_by_tag_name('html')
        if htmls:
            return htmls[0]

    def element_exists(self, **kwargs):
        elements = self._driver.find_elements(*kwargs2selector(**kwargs))
        if elements:
            return True
        return False

    def func_that_detects_new_page(self):
        """
        Return a function that returns true if the browser has navigated
        to a new page.
        """
        old_htmls = self._driver.find_elements_by_tag_name('html')

        def func():
            return (
                self._driver.find_elements_by_tag_name('html') != old_htmls)
        return func

    def __getattr__(self, attr):
        if '_driver' == attr:
            raise AttributeError(attr)
        return getattr(self._driver, attr)
