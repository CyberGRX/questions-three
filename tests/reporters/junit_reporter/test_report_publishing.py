from unittest import TestCase, main

from expects import expect
import junit_xml

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from twin_sister.expects_matchers import contain_key_with_value
from questions_three.reporters.junit_reporter.junit_reporter import \
    JunitReporter, convert_tests
from questions_three.reporters.result_compiler.suite_results \
    import SuiteResults, TestResult


class TestReportPublishing(TestCase):

    def setUp(self):
        EventBroker.reset()
        self.sut = JunitReporter()
        self.sut.activate()
        self.suite_name = 'HowSuite'
        self.published_kwargs = {}
        EventBroker.subscribe(
            event=TestEvent.report_created, func=self.capture_published_kwargs)

    def capture_published_kwargs(self, **kwargs):
        self.published_kwargs = kwargs

    def publish_results(self):
        self.results = SuiteResults()
        self.results.suite_name = self.suite_name
        self.results.tests = [
            TestResult(test_name='Test %d' % n)
            for n in range(4)]
        EventBroker.publish(
            event=TestEvent.suite_results_compiled,
            suite_results=self.results)

    def test_names_file_after_suite(self):
        self.publish_results()
        expect(self.published_kwargs).to(
            contain_key_with_value(
                'report_filename',
                '%s.xml' % self.suite_name))

    def test_names_nameless_suite(self):
        self.suite_name = None
        self.publish_results()
        expect(self.published_kwargs).to(
            contain_key_with_value('report_filename', 'NamelessSuite.xml'))

    def test_publishes_report_content(self):
        self.publish_results()
        suite = junit_xml.TestSuite(
            name=self.suite_name,
            test_cases=convert_tests(self.results.tests))
        expected = junit_xml.TestSuite.to_xml_string([suite])
        expect(self.published_kwargs).to(
            contain_key_with_value('report_content', expected))


if '__main__' == __name__:
    main()
