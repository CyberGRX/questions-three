from unittest import TestCase, main

from expects import expect, have_length
from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from selenium import webdriver
from twin_sister import open_dependency_context
from twin_sister.fakes import EndlessFake

from questions_three_selenium.browser import Browser


class FakeWebdriver(EndlessFake):

    window_handles = 1

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        return self


class TestArtifactGrouping(TestCase):

    def setUp(self):
        self.context = open_dependency_context(supply_env=True)
        fake_webdriver = FakeWebdriver()
        self.context.inject(webdriver, fake_webdriver)
        self.events_captured = []
        EventBroker.subscribe(
            event=TestEvent.artifact_created,
            func=self.capture_event)
        self.sut = Browser()

    def tearDown(self):
        self.context.close()

    def capture_event(self, **kwargs):
        self.events_captured.append(kwargs)

    def extract_artifact_groups(self):
        return [
            e['artifact_group']
            for e in self.events_captured
            if 'artifact_group' in e.keys()]

    def test_all_artifacts_from_same_event_have_same_group(self):
        EventBroker.publish(event=TestEvent.test_failed)
        groups = set(self.extract_artifact_groups())
        expect(groups).to(have_length(1))

    def test_artifacts_from_different_events_have_different_groups(self):
        events = 3
        for n in range(events):
            EventBroker.publish(event=TestEvent.test_failed)
        groups = set(self.extract_artifact_groups())
        expect(groups).to(have_length(events))


if '__main__' == __name__:
    main()
