from datetime import datetime
from junit_xml import TestCase, TestSuite
import os
from twin_sister import dependency
from xml.etree import ElementTree

from questions_three.constants import TestEvent, TestStatus
from questions_three.event_broker import EventBroker, subscribe_event_handlers
from questions_three.module_cfg import config_for_module
from questions_three.vanilla import format_exception,  path_to_entry_script


def convert_status(status):
    if TestStatus.erred == status:
        return 'error'
    if TestStatus.failed == status:
        return 'failure'
    if status in (None, TestStatus.passed):
        return None
    return status.name


def current_time():
    return dependency(datetime).now()


def exception_str(e):
    if e:
        return '(%s) %s' % (type(e), e)
    return ''


def extract_timestamp(test_result):
    if test_result.start_time:
        return test_result.start_time.isoformat()
    return None


def convert_tests(test_results):
    tests = []
    for result in test_results:
        if result.start_time and result.end_time:
            duration = (result.end_time - result.start_time).total_seconds()
        else:
            duration = None
        tc = TestCase(
            name=result.name,
            elapsed_sec=duration,
            status=convert_status(result.status),
            timestamp=extract_timestamp(result))
        if result.exception:
            if TestStatus.failed == result.status:
                tc.add_failure_info(
                    message=exception_str(result.exception),
                    output=format_exception(result.exception))
            elif TestStatus.erred == result.status:
                tc.add_error_info(
                    message=exception_str(result.exception),
                    output=format_exception(result.exception))
            elif TestStatus.skipped == result.status:
                tc.add_skipped_info(
                    message=exception_str(result.exception))
        tests.append(tc)
    return tests


def ci_workspace_path():
    vars = dependency(os).environ
    config = config_for_module(__name__)
    key = config.ci_workspace_env_var
    if key in vars.keys():
        return vars[key]
    return None


def infer_package_name():
    """
    Use the path to the test script to infer a "package" name
    for the Junit report.
    """
    script = dependency(path_to_entry_script)()
    if not script:
        return ''
    script_path, _ = os.path.split(script)
    workspace_mask = ci_workspace_path()
    if workspace_mask:
        script_path = script_path.replace(workspace_mask, '')
    else:
        cwd_mask = dependency(os.getcwd)()
        script_path = script_path.replace(cwd_mask, '')
    name = script_path.replace('/', '.') + '.'
    if name.startswith('.'):
        name = name[1:]
    return name


class JunitReporter:

    REPORTS_DIRECTORY = 'reports'

    def __init__(self):
        self._dummy_test_case = None

    def activate(self):
        subscribe_event_handlers(self)

    def on_suite_erred(self, suite_name, exception=None, **kwargs):
        self._dummy_test_case = TestCase(name=suite_name, status='error')
        if exception:
            self._dummy_test_case.add_error_info(
                message=exception_str(exception),
                output=format_exception(exception))

    def on_suite_results_compiled(self, suite_results, **kwargs):
        suite_name = suite_results.suite_name or 'NamelessSuite'
        test_cases = convert_tests(suite_results.tests)
        if self._dummy_test_case:
            test_cases.append(self._dummy_test_case)
        suite = dependency(TestSuite)(
            name=infer_package_name() + suite_name,
            timestamp=current_time().isoformat(),
            test_cases=test_cases)
        xml_report = ElementTree.tostring(
            suite.build_xml_doc(), encoding='utf-8').decode(encoding='utf-8')
        EventBroker.publish(
            event=TestEvent.report_created,
            suite=suite,
            cases=test_cases,
            report_filename=suite_name + '.xml',
            report_content=xml_report)
