from unittest import TestCase, main

from expects import expect, equal

from questions_three.event_broker import EventBroker
from questions_three.scaffolds.common.activate_reporters import BUILT_IN_REPORTERS

# We expect this import to activate the reporters
import questions_three.scaffolds.test_table  # noqa: F401

ACTIVE_REPORTERS = set([type(subscriber.__self__) for subscriber in EventBroker.get_subscribers()])


class TestDefaultReporters(TestCase):
    def test_contains_all(self):
        expect(ACTIVE_REPORTERS).to(equal(set(BUILT_IN_REPORTERS)))


if "__main__" == __name__:
    main()
