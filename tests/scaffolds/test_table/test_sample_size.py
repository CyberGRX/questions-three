from functools import partial
from unittest import TestCase, main

from expects import expect, equal
from twin_sister.expects_matchers import complain
from twin_sister.fakes import FunctionSpy

from questions_three.constants import TestEvent
from questions_three.exceptions import TestSkipped
from questions_three.event_broker import EventBroker
from questions_three.scaffolds.test_table import execute_test_table


class TestSampleSize(TestCase):
    def tearDown(self):
        EventBroker.reset()

    def test_complains_when_sample_size_is_non_numeric(self):
        table = (("foo", "sample size"), (12, "large"))

        expect(partial(execute_test_table, table=table, func=lambda foo: None)).to(complain(TypeError))

    def test_complains_when_sample_size_is_non_int(self):
        table = (("foo", "sample size"), (12, 3.14))

        expect(partial(execute_test_table, table=table, func=lambda foo: None)).to(complain(TypeError))

    def test_complains_when_sample_size_is_negative(self):
        table = (("foo", "sample size"), (12, -1))

        expect(partial(execute_test_table, table=table, func=lambda foo: None)).to(complain(TypeError))

    def test_repeats_row_specified_number_of_times(self):
        specified_size = 4
        actual_size = 0

        table = (("foo", "sample size"), (1, specified_size))

        def func(foo):
            nonlocal actual_size
            actual_size += 1

        execute_test_table(table=table, func=func)
        expect(actual_size).to(equal(specified_size))

    def check_test_event(self, event, exception=None):
        test_name = "whizzo"
        sample_size = 3
        table = (("test name", "foo", "sample size"), (test_name, "biggles", sample_size))

        def func(foo):
            if exception is not None:
                raise exception

        spy = FunctionSpy()
        EventBroker.subscribe(event=event, func=spy)
        execute_test_table(table=table, func=func)
        for sample in range(sample_size):
            try:
                args, kwargs = spy.call_history[sample]
            except IndexError:
                assert False, f"Too little call history {spy.call_history}"
            expect(kwargs["test_name"]).to(equal(f"{test_name} sample {sample+1}"))

    def test_appends_sequence_number_to_test_name_on_pass(self):
        self.check_test_event(event=TestEvent.test_ended)

    def test_appends_sequence_number_to_test_name_on_start(self):
        self.check_test_event(event=TestEvent.test_started)

    def test_appends_sequence_number_to_test_name_on_error(self):
        self.check_test_event(event=TestEvent.test_erred, exception=RuntimeError("intentional"))

    def test_appends_sequence_number_to_test_name_on_failure(self):
        self.check_test_event(event=TestEvent.test_failed, exception=AssertionError("intentional"))

    def test_appends_sequence_number_to_test_name_on_skip(self):
        self.check_test_event(event=TestEvent.test_skipped, exception=TestSkipped("intentional"))


if "__main__" == __name__:
    main()
