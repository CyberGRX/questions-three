from unittest import TestCase, main
from xml.etree import ElementTree

from expects import expect, contain, have_length
from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker, subscribe_event_handlers
from questions_three.reporters.junit_reporter import JunitReporter
from questions_three.reporters.result_compiler import ResultCompiler
from questions_three.vanilla import format_exception
from twin_sister import close_all_dependency_contexts
from twin_sister.expects_matchers import contain_key_with_value


class TestTestForSuiteSetup(TestCase):
    def setUp(self):
        close_all_dependency_contexts()
        EventBroker.reset()
        subscribe_event_handlers(self)
        self.suite_name = "EarElephant"
        self.xml_report = None
        self.compiler = ResultCompiler()
        self.compiler.activate()
        self.sut = JunitReporter()
        self.sut.activate()

    def publish(self, event, **kwargs):
        EventBroker.publish(event=event, suite_name=self.suite_name, **kwargs)

    def on_report_created(self, report_content, **kwargs):
        self.xml_report = report_content

    def extract_dummy_test(self):
        assert self.xml_report, "No report was generated"
        doc = ElementTree.fromstring(self.xml_report)
        tests = doc.findall(".//testcase")
        expect(tests).to(have_length(1))
        return tests[0]

    def test_named_after_suite(self):
        self.publish(TestEvent.suite_started)
        self.publish(TestEvent.suite_erred, exception=RuntimeError())
        self.publish(TestEvent.suite_ended)
        expect(self.extract_dummy_test().attrib).to(contain_key_with_value("name", self.suite_name))

    def test_status_is_error(self):
        self.publish(TestEvent.suite_started)
        self.publish(TestEvent.suite_erred, exception=RuntimeError())
        self.publish(TestEvent.suite_ended)
        expect(self.extract_dummy_test().attrib).to(contain_key_with_value("status", "error"))

    def test_contains_exception_message(self):
        exception = RuntimeError("failed intentionally")
        self.publish(TestEvent.suite_started)
        self.publish(TestEvent.suite_erred, exception=exception)
        self.publish(TestEvent.suite_ended)
        test = self.extract_dummy_test()
        failures = test.findall("./error")
        expect(failures).to(have_length(1))
        failure = failures[0].attrib
        expect(failure.keys()).to(contain("message"))
        expect(failure["message"]).to(contain(str(exception)))

    def test_contains_exception_stack_trace(self):
        exception = RuntimeError("failed intentionally")
        self.publish(TestEvent.suite_started)
        self.publish(TestEvent.suite_erred, exception=exception)
        self.publish(TestEvent.suite_ended)
        test = self.extract_dummy_test()
        failures = test.findall("./error")
        expect(failures).to(have_length(1))
        failure = failures[0]
        expect(failure.text).to(contain(format_exception(exception)))


if "__main__" == __name__:
    main()
