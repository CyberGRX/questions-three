from copy import copy
import os
from unittest import TestCase, main

from expects import expect, equal, have_length
import junit_xml
from twin_sister import open_dependency_context

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.reporters.junit_reporter import JunitReporter
from questions_three.reporters.result_compiler.suite_results import \
    SuiteResults
from twin_sister.fakes import MasterSpy
from questions_three.vanilla import path_to_entry_script


class TestExtendedSuiteName(TestCase):

    def setUp(self):
        EventBroker.reset()
        self.context = open_dependency_context(supply_env=True)
        defanged = copy(junit_xml.TestSuite)
        defanged.to_xml_string = lambda *args, **kwargs: ''
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

    def test_prepends_path_to_suite_name(self):
        path = 'one/two/three'
        self.context.inject(
            path_to_entry_script,
            lambda: os.path.join(path, 'test_tea.py'))
        suite_name = 'NestedSuite'
        self.results.suite_name = suite_name
        self.publish_results()
        report = self.retrieve_report()
        prefix = '.'.join(path.split('/'))
        expect(report.name).to(equal('.'.join((prefix, suite_name))))

    def test_masks_path_to_workspace_if_set(self):
        workspace_path = '/path/to/workspace'
        relative_path = 'tests/something'
        suite_name = 'MyTest'
        self.results.suite_name = suite_name
        self.context.os.environ['workspace_env_var'] = 'WORKSPACE'
        self.context.os.environ['WORKSPACE'] = workspace_path
        self.context.inject(
            path_to_entry_script,
            lambda: os.path.join(
                workspace_path, relative_path, 'my_test.py'))
        self.publish_results()
        report = self.retrieve_report()
        prefix = relative_path.replace('/', '.')
        expect(report.name).to(equal(prefix + '.' + suite_name))

    def test_masks_path_to_cwd_if_workspace_unset(self):
        fake_cwd = '/Here/I/stand'
        relative_path = 'yadda/dada/yogurt'
        suite_name = 'Worms'
        self.results.suite_name = suite_name
        self.context.inject(os.getcwd, lambda: fake_cwd)
        self.context.inject(
            path_to_entry_script,
            lambda: os.path.join(
                fake_cwd, relative_path, 'whatever.py'))
        self.publish_results()
        report = self.retrieve_report()
        prefix = relative_path.replace('/', '.')
        expect(report.name).to(equal(prefix + '.' + suite_name))

    def test_handles_invocation_from_terminal_gracefully(self):
        suite_name = 'SomethingSuite'
        self.context.inject(path_to_entry_script, lambda: None)
        self.results.suite_name = suite_name
        self.publish_results()
        report = self.retrieve_report()
        expect(report.name).to(equal(suite_name))


if '__main__' == __name__:
    main()
