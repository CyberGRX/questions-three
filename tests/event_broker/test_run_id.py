from unittest import TestCase, main

from expects import expect, equal
from twin_sister import open_dependency_context

from questions_three.event_broker import EventBroker
from questions_three.module_cfg import config_for_module


class TestRunId(TestCase):

    def setUp(self):
        EventBroker.reset()
        self.context = open_dependency_context(
            supply_logging=True, supply_env=True)

    def tearDown(self):
        self.context.close

    def test_sends_run_id_as_kwarg_with_arbitrary_event(self):
        event = 'shindig'
        planted = '4922222'
        retrieved = None
        self.context.set_env(TEST_RUN_ID=planted)

        def spy(*, run_id, **kwargs):
            nonlocal retrieved
            retrieved = run_id

        EventBroker.subscribe(event=event, func=spy)
        EventBroker.publish(event=event)
        expect(retrieved).to(equal(planted))

    def test_uses_module_default_when_not_set_in_env(self):
        event = 'spamorama'
        conf = config_for_module('questions_three.event_broker')
        retrieved = None

        def spy(*, run_id, **kwargs):
            nonlocal retrieved
            retrieved = run_id

        EventBroker.subscribe(event=event, func=spy)
        EventBroker.publish(event=event)
        expect(retrieved).to(equal(conf.test_run_id))


if '__main__' == __name__:
    main()
