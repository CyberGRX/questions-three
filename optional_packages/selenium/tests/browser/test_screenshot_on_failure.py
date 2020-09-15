from contextlib import contextmanager
from unittest import TestCase, main

from expects import expect
from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from twin_sister.expects_matchers import contain_key_with_value
from twin_sister.fakes import EndlessFake
from selenium import webdriver
from twin_sister import open_dependency_context

from questions_three_selenium.browser import Browser


class FakeFile:
    @contextmanager
    def open(self, *args, **kwargs):
        yield self

    def read(self):
        return "{}"


class FakeWebdriver(EndlessFake):
    def __init__(self):
        super().__init__()
        self.png_bytes = None
        self.open_windows = 1

    def get_screenshot_as_png(self):
        return self.png_bytes

    def _window_handles(self):
        return ["spam" for n in range(self.open_windows)]

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        if "window_handles" == name:
            return self._window_handles()
        return self


class TestScreenshotOnFailure(TestCase):
    def setUp(self):
        EventBroker.reset()
        EventBroker.subscribe(event=TestEvent.artifact_created, func=self.catch_artifact_event)
        self.context = open_dependency_context(supply_env=True, supply_fs=True)
        self.fake_webdriver = FakeWebdriver()
        self.context.inject(webdriver, self.fake_webdriver)
        self.sut = Browser()
        self.artifact_events = []

    def tearDown(self):
        self.context.close()

    def catch_artifact_event(self, **kwargs):
        self.artifact_events.append(kwargs)

    def artifact_event_kwargs(self):
        screenshot_events = [
            e for e in self.artifact_events if "artifact_type" in e.keys() and e["artifact_type"] == "screenshot"
        ]
        count = len(screenshot_events)
        if 0 == count:
            return {}
        if 1 == count:
            return screenshot_events[0]
        raise RuntimeError("Found %d screenshot events" % count)

    def test_publishes_screenshot_on_suite_erred(self):
        suite_name = "Jerry"
        EventBroker.publish(event=TestEvent.suite_erred, suite_name=suite_name)
        expect(self.artifact_event_kwargs()).to(contain_key_with_value("suite_name", suite_name))

    def test_publishes_screenshot_on_test_erred_with_test_name(self):
        test_name = "Tom"
        EventBroker.publish(event=TestEvent.test_erred, test_name=test_name)
        expect(self.artifact_event_kwargs()).to(contain_key_with_value("test_name", test_name))

    def test_publishes_screenshot_on_test_failed_with_test_name(self):
        test_name = "Robin"
        EventBroker.publish(event=TestEvent.test_failed, test_name=test_name)
        expect(self.artifact_event_kwargs()).to(contain_key_with_value("test_name", test_name))

    def test_screenshot_contains_bytes_from_webdriver(self):
        expected = b"bbbbbbbbbbbbb"
        self.fake_webdriver.png_bytes = expected
        EventBroker.publish(event=TestEvent.test_failed)
        expect(self.artifact_event_kwargs()).to(contain_key_with_value("artifact", expected))

    def test_mime_type_is_png(self):
        EventBroker.publish(event=TestEvent.test_failed)
        expect(self.artifact_event_kwargs()).to(contain_key_with_value("artifact_mime_type", "image/png"))

    def test_artifact_type_is_screenshot(self):
        EventBroker.publish(event=TestEvent.test_failed)
        expect(self.artifact_event_kwargs()).to(contain_key_with_value("artifact_type", "screenshot"))

    def test_does_not_take_screenshot_if_browser_is_closed(self):
        self.fake_webdriver.open_windows = 0
        EventBroker.publish(event=TestEvent.test_failed)
        assert not self.artifact_event_kwargs(), "A screenshot event was published inappropriately"


if "__main__" == __name__:
    main()
