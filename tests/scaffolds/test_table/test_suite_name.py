from unittest import TestCase, main

from expects import expect, equal

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.scaffolds.test_table import execute_test_table


class TestSuiteName(TestCase):

    def tearDown(self):
        EventBroker.reset()

    def test_uses_suite_name_when_specified(self):
        specified_suite_name = 'HoneymoonSuite'
        published_suite_name = None

        def spy(*, suite_name, **kwargs):
            nonlocal published_suite_name
            published_suite_name = suite_name

        EventBroker.subscribe(event=TestEvent.suite_started, func=spy)
        execute_test_table(
            suite_name=specified_suite_name,
            table=(('spam',), ('spam',)), func=lambda spam: None)
        expect(published_suite_name).to(equal(specified_suite_name))

    def test_uses_function_name_when_no_suite_name_specified(self):
        published_suite_name = None

        def spy(*, suite_name, **kwargs):
            nonlocal published_suite_name
            published_suite_name = suite_name

        def fancy_procedure(*, spam):
            pass

        EventBroker.subscribe(event=TestEvent.suite_started, func=spy)
        execute_test_table(
            table=(('spam',), ('spam',)), func=fancy_procedure)
        expect(published_suite_name).to(equal(fancy_procedure.__name__))


if '__main__' == __name__:
    main()
