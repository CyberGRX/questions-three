from unittest import TestCase, main

from expects import expect, be, be_empty, be_within, equal, have_length
from twin_sister.fakes import FunctionSpy

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.exceptions import TestSkipped
from questions_three.scaffolds.test_table import execute_test_table

ALL_EVENTS = list(TestEvent)
SUITE_NAME = "SpammySuite"
TEST_NAMES = ("first test", "second test")


def execute(func=lambda item: None):
    execute_test_table(
        table=(("item", "test name"), ("spam", TEST_NAMES[0]), ("eggs", TEST_NAMES[1])),
        func=func,
        suite_name=SUITE_NAME,
    )


def events_with_type(call_history, specified_type):
    return [published for published in call_history if published[1]["event"] == specified_type]


class TestEventPublishing(TestCase):
    def tearDown(self):
        EventBroker.reset()

    def test_publishes_suite_started_first(self):
        spy = FunctionSpy()
        EventBroker.subscribe(events=ALL_EVENTS, func=spy)
        execute()
        args, kwargs = spy.call_history[0]
        expect(kwargs["event"]).to(equal(TestEvent.suite_started))

    def test_publishes_suite_started_exactly_once(self):
        spy = FunctionSpy()
        EventBroker.subscribe(events=ALL_EVENTS, func=spy)
        execute()
        expect(events_with_type(spy.call_history, TestEvent.suite_started)).to(have_length(1))

    def test_publishes_suite_ended_with_suite_name(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.suite_ended, func=spy)
        execute()
        expect(spy["suite_name"]).to(equal(SUITE_NAME))

    def test_publishes_suite_ended_last(self):
        spy = FunctionSpy()
        EventBroker.subscribe(events=ALL_EVENTS, func=spy)
        execute()
        args, kwargs = spy.call_history[-1]
        expect(kwargs["event"]).to(equal(TestEvent.suite_ended))

    def test_publishes_suite_ended_exactly_once(self):
        spy = FunctionSpy()
        EventBroker.subscribe(events=ALL_EVENTS, func=spy)
        execute()
        expect(events_with_type(spy.call_history, TestEvent.suite_ended)).to(have_length(1))

    def test_pubishes_test_started_with_test_name(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_started, func=spy)
        execute()
        expect([call[1]["test_name"] for call in spy.call_history]).to(equal(list(TEST_NAMES)))

    def test_publishes_test_started_with_suite_name(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_started, func=spy)
        execute()
        expect(spy["suite_name"]).to(equal(SUITE_NAME))

    def test_publishes_test_started_for_each_row(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_started, func=spy)
        execute()
        expect(spy.call_history).to(have_length(len(TEST_NAMES)))

    def test_publishes_test_ended_with_test_name(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_ended, func=spy)
        execute()
        expect([call[1]["test_name"] for call in spy.call_history]).to(equal(list(TEST_NAMES)))

    def test_publishes_test_ended_with_suite_name(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_ended, func=spy)
        execute()
        expect(spy["suite_name"]).to(equal(SUITE_NAME))

    def test_publishes_test_ended_for_each_row(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_ended, func=spy)
        execute()
        expect(spy.call_history).to(have_length(len(TEST_NAMES)))

    def test_publishes_test_started_before_test_ended(self):
        test_started = False

        def start_listener(**kwargs):
            nonlocal test_started
            test_started = True

        def end_listener(**kwargs):
            nonlocal test_started
            assert test_started, "Test was not started"
            test_started = False

        EventBroker.subscribe(event=TestEvent.test_started, func=start_listener)
        EventBroker.subscribe(event=TestEvent.test_ended, func=end_listener)
        execute()

    def test_publishes_test_ended_after_test_skipped(self):
        table = (("thing",), (14,))
        test_skipped = False
        test_ended = False
        ended_before_skipped = False

        def ended(**kwargs):
            nonlocal ended_before_skipped
            nonlocal test_ended
            ended_before_skipped = not test_skipped
            test_ended = True

        def skipped(**kwargs):
            nonlocal test_skipped
            test_skipped = True

        def test_func(thing):
            raise TestSkipped("intentional")

        EventBroker.subscribe(event=TestEvent.test_ended, func=ended)
        EventBroker.subscribe(event=TestEvent.test_skipped, func=skipped)
        execute_test_table(table=table, func=test_func)
        assert test_ended, "Test was not ended"
        assert not ended_before_skipped, "Test ended before it was skipped"

    def test_publishes_test_ended_after_test_failed(self):
        table = (("thing",), (14,))
        test_failed = False
        test_ended = False
        ended_before_failed = False

        def ended(**kwargs):
            nonlocal ended_before_failed
            nonlocal test_ended
            test_ended = True
            ended_before_failed = not test_failed

        def failed(**kwargs):
            nonlocal test_failed
            nonlocal ended_before_failed
            test_failed = True

        def test_func(thing):
            assert False, "An assertion error escaped"

        EventBroker.subscribe(event=TestEvent.test_ended, func=ended)
        EventBroker.subscribe(event=TestEvent.test_failed, func=failed)
        execute_test_table(table=table, func=test_func)
        assert test_ended, "Test was not ended"
        assert not ended_before_failed, "Test ended before it failed"

    def test_publishes_test_ended_after_test_erred(self):
        table = (("thing",), (14,))
        test_erred = False
        test_ended = False
        ended_before_erred = False

        def ended(**kwargs):
            nonlocal ended_before_erred
            nonlocal test_ended
            test_ended = True
            ended_before_erred = not test_erred

        def erred(**kwargs):
            nonlocal test_erred
            nonlocal ended_before_erred
            test_erred = True

        def test_func(thing):
            raise RuntimeError("An exception escaped the test block")

        EventBroker.subscribe(event=TestEvent.test_ended, func=ended)
        EventBroker.subscribe(event=TestEvent.test_erred, func=erred)
        execute_test_table(table=table, func=test_func)
        assert test_ended, "Test was not ended"
        assert not ended_before_erred, "Test ended before it erred"

    def test_publishes_test_skipped_with_test_name(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_skipped, func=spy)

        def test_func(item):
            raise TestSkipped("intentional")

        execute(func=test_func)
        expect(spy["test_name"]).to(equal(TEST_NAMES[-1]))

    def test_publishes_test_skipped_with_exception(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_skipped, func=spy)
        raised = TestSkipped("spammy spam spam")

        def test_func(item):
            raise raised

        execute(func=test_func)
        expect(spy["exception"]).to(be(raised))

    def test_publishes_test_skipped_with_suite_name(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_skipped, func=spy)

        def test_func(item):
            raise TestSkipped("intentional")

        execute(func=test_func)
        expect(spy["suite_name"]).to(equal(SUITE_NAME))

    def test_publishes_test_erred_with_test_name(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_erred, func=spy)

        def test_func(item):
            raise Exception("intentional")

        execute(func=test_func)
        expect(spy["test_name"]).to(equal(TEST_NAMES[-1]))

    def test_publishes_test_erred_with_suite_name(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_erred, func=spy)

        def test_func(item):
            raise RuntimeError("SPAMoni")

        execute(func=test_func)
        expect(spy["suite_name"]).to(equal(SUITE_NAME))

    def test_publishes_test_erred_with_exception(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_erred, func=spy)
        raised = Exception("spammy spam spam")

        def test_func(item):
            raise raised

        execute(func=test_func)
        expect(spy["exception"]).to(be(raised))

    def test_publishes_test_failed_with_test_name(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_failed, func=spy)

        def test_func(item):
            assert False, "Oh no, you don't"

        execute(func=test_func)
        expect(spy["test_name"]).to(equal(TEST_NAMES[-1]))

    def test_publishes_test_failed_with_suite_name(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_failed, func=spy)

        def test_func(item):
            assert False, "Albatross!"

        execute(func=test_func)
        expect(spy["suite_name"]).to(equal(SUITE_NAME))

    def test_publishes_test_failed_with_exception(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_failed, func=spy)
        raised = AssertionError("spammy spam spam")

        def test_func(item):
            raise raised

        execute(func=test_func)
        expect(spy["exception"]).to(be(raised))

    def test_publishes_sample_measured_with_suite_name(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.sample_measured, func=spy)
        execute()
        expect(spy["suite_name"]).to(equal(SUITE_NAME))

    def test_publishes_sample_measured_with_test_name(self):
        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.sample_measured, func=spy)
        execute()
        expect(spy["test_name"]).to(equal(TEST_NAMES[-1]))

    def test_publishes_sample_measured_with_sample_parameters(self):
        params = {"foo": 14, "bar": "all night", "baz": {"spam": "you betcha"}}
        table = (list(params.keys()), list(params.values()))

        def test_func(foo, bar, baz):
            pass

        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.sample_measured, func=spy)
        execute_test_table(table=table, func=test_func)
        expect(spy["sample_parameters"]).to(equal(params))

    def test_publishes_sample_measured_with_execution_time(self):
        start_spy = FunctionSpy()
        measure_spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.test_started, func=start_spy)
        EventBroker.subscribe(event=TestEvent.sample_measured, func=measure_spy)
        execute()
        start_time = start_spy["event_time"]
        end_time = measure_spy["event_time"]
        actual_time = (end_time - start_time).total_seconds()
        reported_time = measure_spy["sample_execution_seconds"]
        expect(abs(actual_time - reported_time)).to(be_within(0, 0.1))

    def test_does_not_publish_sample_measured_if_skipped(self):
        def test_func(item):
            raise TestSkipped("yadda")

        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.sample_measured, func=spy)
        execute(func=test_func)
        expect(spy.call_history).to(be_empty)

    def test_does_not_publish_sample_measured_if_failed(self):
        def test_func(item):
            assert False, "yadda"

        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.sample_measured, func=spy)
        execute(func=test_func)
        expect(spy.call_history).to(be_empty)

    def test_does_not_publish_sample_measured_if_erred(self):
        def test_func(item):
            raise Exception("Hello!")

        spy = FunctionSpy()
        EventBroker.subscribe(event=TestEvent.sample_measured, func=spy)
        execute(func=test_func)
        expect(spy.call_history).to(be_empty)


if "__main__" == __name__:
    main()
