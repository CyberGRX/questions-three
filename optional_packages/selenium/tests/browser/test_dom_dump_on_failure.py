from unittest import TestCase, main

from expects import expect, be
from selenium import webdriver
from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from twin_sister.expects_matchers import contain_key_with_value
from twin_sister.fakes import EndlessFake
from questions_three_selenium.dom_dumper.dump_dom import dump_dom
from twin_sister import open_dependency_context

from questions_three_selenium.browser import Browser


class FakeWebdriver(EndlessFake):
    def __init__(self):
        super().__init__()
        self.window_handles = 1  # pretend to have an open window

    def __call__(self, *args, **kwargs):
        return self


class TestDomDumpOnFailure(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True)
        EventBroker.reset()
        EventBroker.subscribe(event=TestEvent.artifact_created, func=self.catch_artifact_event)
        self.artifact_events_caught = []
        self.fake_webdriver = FakeWebdriver()
        self.context.inject(webdriver, self.fake_webdriver)
        self.fake_dump = "yaddayaddayadda"
        self.context.inject(dump_dom, lambda x: self.fake_dump)
        self.sut = Browser()

    def tearDown(self):
        self.context.close()

    def catch_artifact_event(self, **kwargs):
        self.artifact_events_caught.append(kwargs)

    def caught_dom_dump_events(self):
        return [
            e for e in self.artifact_events_caught if "artifact_type" in e.keys() and "dom_dump" == e["artifact_type"]
        ]

    def caught_dom_dump_kwargs(self):
        events = self.caught_dom_dump_events()
        count = len(events)
        if 0 == count:
            raise AssertionError("No dom_dump artifacts were published")
        if 1 == count:
            return events[0]
        raise AssertionError("%d dom_dump artifacts were published" % count)

    def test_publishes_dump_on_suite_erred(self):
        EventBroker.publish(event=TestEvent.suite_erred)
        expect(self.caught_dom_dump_kwargs()).to(contain_key_with_value("artifact", self.fake_dump))

    def test_sends_self_to_dom_dump(self):
        arg = None

        def fake_dump(a):
            nonlocal arg
            arg = a

        self.context.inject(dump_dom, fake_dump)
        EventBroker.publish(event=TestEvent.suite_erred)
        expect(arg).to(be(self.sut))

    def test_publishes_dump_on_test_erred(self):
        EventBroker.publish(event=TestEvent.test_erred)
        expect(self.caught_dom_dump_kwargs()).to(contain_key_with_value("artifact", self.fake_dump))

    def test_publishes_dump_on_test_failed(self):
        EventBroker.publish(event=TestEvent.test_failed)
        expect(self.caught_dom_dump_kwargs()).to(contain_key_with_value("artifact", self.fake_dump))

    def test_includes_suite_name_on_suite_erred(self):
        suite_name = "SuiteT"
        EventBroker.publish(event=TestEvent.suite_erred, suite_name=suite_name)
        expect(self.caught_dom_dump_kwargs()).to(contain_key_with_value("suite_name", suite_name))

    def test_includes_suite_name_on_test_failed(self):
        suite_name = "SuiteT"
        EventBroker.publish(event=TestEvent.test_failed, suite_name=suite_name)
        expect(self.caught_dom_dump_kwargs()).to(contain_key_with_value("suite_name", suite_name))

    def test_includes_test_name(self):
        test_name = "watch this"
        EventBroker.publish(event=TestEvent.test_erred, test_name=test_name)
        expect(self.caught_dom_dump_kwargs()).to(contain_key_with_value("test_name", test_name))

    def test_artifact_type_is_dom_dump(self):
        EventBroker.publish(event=TestEvent.suite_erred)
        expect(self.caught_dom_dump_kwargs()).to(contain_key_with_value("artifact_type", "dom_dump"))

    def test_mime_type_is_html(self):
        EventBroker.publish(event=TestEvent.suite_erred)
        expect(self.caught_dom_dump_kwargs()).to(contain_key_with_value("artifact_mime_type", "text/html"))


if "__main__" == __name__:
    main()
