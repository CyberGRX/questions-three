from unittest import TestCase, main

from expects import expect, be_a, contain, equal, have_length, raise_error

from questions_three.constants import TestEvent, TestStatus
from questions_three.event_broker import EventBroker
from questions_three.reporters.result_compiler import ResultCompiler


class Subscriber:

    def __init__(self):
        self.results = None
        EventBroker.subscribe(
            event=TestEvent.suite_results_compiled, func=self.receiver)

    def receiver(self, suite_results, **kwargs):
        self.results = suite_results


def start_suite(suite_name='spam'):
    EventBroker.publish(event=TestEvent.suite_started, suite_name=suite_name)


def end_suite(suite_name='spam'):
    EventBroker.publish(event=TestEvent.suite_ended, suite_name=suite_name)


def start_test(test_name='spam'):
    EventBroker.publish(event=TestEvent.test_started, test_name=test_name)


def end_test(test_name='spam'):
    EventBroker.publish(event=TestEvent.test_ended, test_name=test_name)


def err_test(test_name, exception=None):
    EventBroker.publish(
        event=TestEvent.test_erred, test_name=test_name, exception=exception)


def fail_test(test_name, exception=None):
    EventBroker.publish(
        event=TestEvent.test_failed, test_name=test_name, exception=exception)


def skip_test(test_name, exception=None):
    EventBroker.publish(
        event=TestEvent.test_skipped, test_name=test_name, exception=exception)


class TestResultCompiler(TestCase):

    def setUp(self):
        EventBroker.reset()
        self.subscriber = Subscriber()
        self.sut = ResultCompiler()
        self.sut.activate()

    def retrieve_results(self):
        results = self.subscriber.results
        assert results is not None, 'No results were published'
        return results

    def test_puts_suite_name_in_suite(self):
        name = 'Deloris'
        start_suite(name)
        end_suite(name)
        expect(self.retrieve_results().suite_name).to(equal(name))

    def test_puts_test_name_in_first_test(self):
        name = 'Sam Samson'
        start_suite()
        start_test(name)
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        expect(results.tests[0].name).to(equal(name))

    def test_puts_test_name_in_last_test(self):
        name = 'Ruth'
        start_suite()
        for n in range(5):
            start_test()
        start_test(name)
        end_suite()
        results = self.retrieve_results()
        expect(results.tests[-1].name).to(equal(name))

    def test_test_status_pass(self):
        start_suite()
        start_test()
        end_test()
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        expect(results.tests[0].status).to(equal(TestStatus.passed))

    def test_test_status_fail(self):
        name = 'Robin'
        start_suite()
        start_test(name)
        fail_test(name)
        end_test(name)
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        expect(results.tests[0].status).to(equal(TestStatus.failed))

    def test_attaches_exception_to_failed_test(self):
        name = 'Ximinez'
        exception = RuntimeError('intentional')
        start_suite()
        start_test(name)
        fail_test(name, exception=exception)
        end_test(name)
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        expect(results.tests[0].exception).to(equal(exception))

    def test_handles_test_failed_event_without_exception_gracefully(self):
        name = 'susan'
        start_suite()
        start_test(name)

        def attempt():
            EventBroker.publish(
                event=TestEvent.test_failed, test_name=name,
                exception=RuntimeError())

        expect(attempt).not_to(raise_error(Exception))
        end_test(name)
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        expect(results.tests[0].status).to(equal(TestStatus.failed))

    def test_test_status_err(self):
        name = 'Galahad'
        start_suite()
        start_test(name)
        err_test(name)
        end_test(name)
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        expect(results.tests[0].status).to(equal(TestStatus.erred))

    def test_attaches_exception_to_errant_test(self):
        name = 'Biggles'
        exception = RuntimeError('intentional')
        start_suite()
        start_test(name)
        err_test(name, exception=exception)
        end_test(name)
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        expect(results.tests[0].exception).to(equal(exception))

    def test_test_status_skip(self):
        name = 'The Vicious Chicken of Bristol'
        start_suite()
        start_test(name)
        skip_test(name)
        end_test(name)
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        expect(results.tests[0].status).to(equal(TestStatus.skipped))

    def test_attaches_exception_to_skipped_test(self):
        name = 'Fang'
        exception = RuntimeError('intentional')
        start_suite()
        start_test(name)
        skip_test(name, exception=exception)
        end_test(name)
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        expect(results.tests[0].exception).to(equal(exception))

    def test_suite_status_pass(self):
        start_suite()
        start_test()
        end_test()
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        expect(results.tests[0].status).to(equal(TestStatus.passed))

    def test_attaches_exception_to_errant_suite(self):
        suite_name = 'SPAMmy Suite'
        exception = RuntimeError("I don't like SPAM!")
        start_suite(suite_name)
        EventBroker.publish(
            event=TestEvent.suite_erred,
            suite_name=suite_name, exception=exception)
        end_suite()
        expect(self.retrieve_results().suite_exception).to(equal(exception))

    def test_creates_suite_exception_if_none_specified(self):
        suite_name = 'Squirelly Suite'
        start_suite(suite_name)
        EventBroker.publish(
            event=TestEvent.suite_erred, suite_name=suite_name,
            exception=RuntimeError())
        end_suite()
        expect(self.retrieve_results().suite_exception).to(be_a(Exception))

    def test_suite_exception_is_none_if_suite_does_not_err(self):
        test_name = 'Eliaphaz'
        start_suite()
        start_test(test_name)
        err_test(test_name)
        end_test(test_name)
        end_suite()
        expect(self.retrieve_results().suite_exception).to(equal(None))

    def test_attaches_artifact_to_named_test(self):
        artifact = b'bbbbbbbbbbbbbbbbbb'
        name = 'Bobbb'
        start_suite()
        start_test(name)
        EventBroker.publish(
            event=TestEvent.artifact_created, test_name=name,
            artifact=artifact)
        end_test(name)
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        expect(results.tests[0].artifacts).to(contain(artifact))

    def test_attaches_artifact_to_suite_when_no_test_named(self):
        artifact = b'fffffffffffffff'
        start_suite()
        EventBroker.publish(
            event=TestEvent.artifact_created, artifact=artifact)
        end_suite()
        results = self.retrieve_results()
        expect(results.artifacts).to(contain(artifact))

    def test_creates_missing_test_on_test_failed(self):
        test_name = 'oops'
        start_suite()
        fail_test(test_name)
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        test = results.tests[0]
        expect(test.name).to(equal(test_name))

    def test_creates_missing_test_on_test_erred(self):
        test_name = 'oops'
        start_suite()
        err_test(test_name)
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        test = results.tests[0]
        expect(test.name).to(equal(test_name))

    def test_creates_missing_test_on_test_skipped(self):
        test_name = 'oops'
        start_suite()
        skip_test(test_name)
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        test = results.tests[0]
        expect(test.name).to(equal(test_name))

    def test_creates_missing_test_on_artifact_with_test_name(self):
        test_name = 'oops'
        start_suite()
        EventBroker.publish(
            event=TestEvent.artifact_created, test_name=test_name,
            artifact='this')
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        test = results.tests[0]
        expect(test.name).to(equal(test_name))

    def test_does_not_create_duplicate_test_on_test_started(self):
        name = 'spam'
        start_suite()
        fail_test(name)
        start_test(name)
        end_suite()
        expect(self.retrieve_results().tests).to(have_length(1))

    def test_test_started_but_not_ended_has_status_running(self):
        start_suite()
        start_test()
        end_suite()
        results = self.retrieve_results()
        expect(results.tests).to(have_length(1))
        expect(results.tests[0].status).to(equal(TestStatus.running))


if '__main__' == __name__:
    main()
