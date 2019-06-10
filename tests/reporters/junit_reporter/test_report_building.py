from copy import copy
from datetime import datetime
from unittest import TestCase, main

from expects import expect, contain, equal, end_with, have_length
import junit_xml
from twin_sister import open_dependency_context

from questions_three.constants import TestEvent, TestStatus
from questions_three.event_broker import EventBroker
from questions_three.reporters.junit_reporter import JunitReporter
from questions_three.reporters.result_compiler.suite_results \
    import SuiteResults, TestResult
from twin_sister.fakes import FakeDatetime, MasterSpy
from questions_three.vanilla import format_exception


def return_empty_string(*args, **kwargs):
    return ''


class TestReportBuilding(TestCase):

    def setUp(self):
        EventBroker.reset()
        self.context = open_dependency_context()
        defanged = copy(junit_xml.TestSuite)
        defanged.to_xml_string = return_empty_string
        self.spy = MasterSpy(defanged, affect_only_functions=False)
        self.context.inject(junit_xml.TestSuite, self.spy)
        self.results = SuiteResults()
        self.sut = JunitReporter()
        self.sut.activate()

    def tearDown(self):
        self.context.close()

    def publish_results(self):
        EventBroker.publish(
            event=TestEvent.suite_results_compiled, suite_results=self.results)

    def retrieve_report(self):
        # Our master spy monitors the TestSuite class,
        # so each of its return value spies monitors an instance of the class.
        spies = self.spy.return_value_spies
        # We expect only one instance to have been created
        expect(spies).to(have_length(1))
        return spies[0].unwrap_spy_target()

    def test_sets_suite_name(self):
        expected = 'Dingo'
        self.results.suite_name = expected
        self.publish_results()
        report = self.retrieve_report()
        expect(report.name).to(end_with(expected))

    def test_sets_suite_timestamp_to_suite_start_time(self):
        expected = datetime.fromtimestamp(1516899650.147505)
        fake_time = FakeDatetime()
        fake_time.fixed_time = expected
        self.context.inject(datetime, fake_time)
        self.publish_results()
        report = self.retrieve_report()
        expect(report.timestamp).to(equal(expected.isoformat()))

    def test_adds_correct_number_of_test_cases(self):
        expected = 42
        self.results.tests = [
            TestResult(test_name=str(n)) for n in range(expected)]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases).to(have_length(expected))

    def test_sets_test_name(self):
        expected = 'Son of SPAM'
        self.results.tests = [TestResult(test_name=expected)]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases).to(have_length(1))
        expect(report.test_cases[0].name).to(equal(expected))

    def test_sets_test_timestamp_to_test_start_time(self):
        expected = datetime.fromtimestamp(1516900087.97135)
        result = TestResult(test_name='spam')
        result.start_time = expected
        self.results.tests = [result]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases[0].timestamp).to(
            equal(expected.isoformat()))

    def test_sets_test_elapsed_sec(self):
        start_time = datetime.fromtimestamp(1516900087.97135)
        end_time = datetime.fromtimestamp(1516900089.52436)
        result = TestResult(test_name='bacon')
        result.start_time = start_time
        result.end_time = end_time
        self.results.tests = [result]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases[0].elapsed_sec).to(
            equal((end_time - start_time).total_seconds()))

    def test_does_not_set_status_for_passed_test(self):
        result = TestResult(test_name='spam')
        result.status = TestStatus.passed
        self.results.tests = [result]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases).to(have_length(1))
        expect(report.test_cases[0].status).to(equal(None))

    def test_sets_status_for_failed_test(self):
        result = TestResult(test_name='spam')
        result.status = TestStatus.failed
        self.results.tests = [result]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases).to(have_length(1))
        expect(report.test_cases[0].status).to(equal('failure'))

    def test_sets_status_for_errant_test(self):
        result = TestResult(test_name='spam')
        result.status = TestStatus.erred
        self.results.tests = [result]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases).to(have_length(1))
        expect(report.test_cases[0].status).to(equal('error'))

    def test_sets_status_for_skipped_test(self):
        result = TestResult(test_name='spam')
        result.status = TestStatus.skipped
        self.results.tests = [result]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases).to(have_length(1))
        expect(report.test_cases[0].status).to(equal('skipped'))

    def test_does_not_set_error_message_for_passed_test(self):
        result = TestResult(test_name='spam')
        result.status = TestStatus.passed
        self.results.tests = [result]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases).to(have_length(1))
        expect(report.test_cases[0].error_message).to(equal(None))

    def test_does_not_set_failure_message_for_passed_test(self):
        result = TestResult(test_name='spam')
        result.status = TestStatus.passed
        self.results.tests = [result]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases).to(have_length(1))
        expect(report.test_cases[0].failure_message).to(equal(None))

    def test_sets_message_for_failed_test(self):
        expected = 'I broke it real good'
        result = TestResult(test_name='spam')
        result.status = TestStatus.failed
        result.exception = Exception(expected)
        self.results.tests = [result]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases).to(have_length(1))
        expect(report.test_cases[0].failure_message).to(contain(expected))

    def test_sets_output_for_failed_test(self):
        exception = RuntimeError('Failed intentionally')
        result = TestResult(test_name='spam')
        result.status = TestStatus.failed
        result.exception = exception
        self.results.tests = [result]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases).to(have_length(1))
        expect(report.test_cases[0].failure_output).to(
            contain(format_exception(exception)))

    def test_sets_message_for_errant_test(self):
        expected = 'I tried to think but nothing happened'
        result = TestResult(test_name='spam')
        result.status = TestStatus.erred
        result.exception = Exception(expected)
        self.results.tests = [result]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases).to(have_length(1))
        expect(report.test_cases[0].error_message).to(contain(expected))

    def test_sets_output_for_errant_test(self):
        exception = RuntimeError('Failed intentionally')
        result = TestResult(test_name='spam')
        result.status = TestStatus.erred
        result.exception = exception
        self.results.tests = [result]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases).to(have_length(1))
        expect(report.test_cases[0].error_output).to(
            contain(format_exception(exception)))

    def test_sets_message_for_skipped_test(self):
        expected = 'Run away!'
        result = TestResult(test_name='spam')
        result.status = TestStatus.skipped
        result.exception = Exception(expected)
        self.results.tests = [result]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases).to(have_length(1))
        expect(report.test_cases[0].skipped_message).to(contain(expected))

    def test_does_not_set_output_for_skipped_test(self):
        exception = RuntimeError('Failed intentionally')
        result = TestResult(test_name='spam')
        result.status = TestStatus.skipped
        result.exception = exception
        self.results.tests = [result]
        self.publish_results()
        report = self.retrieve_report()
        expect(report.test_cases).to(have_length(1))
        expect(report.test_cases[0].skipped_output).to(equal(None))


if '__main__' == __name__:
    main()
