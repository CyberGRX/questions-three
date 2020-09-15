import os
from unittest import TestCase, main
from xml.etree import ElementTree

from expects import expect, equal
from pyfakefs import fake_filesystem as fakefs
from twin_sister import open_dependency_context

from questions_three.ci.junit2jenkins_status import ERROR, FAIL, PASS, junit2jenkins_status
from twin_sister.expects_matchers import raise_ex


ParseError = ElementTree.ParseError


class TestJunit2Jenkins(TestCase):
    def setUp(self):
        self.reports_path = "somewhere/over/the/rainbow"
        self.context = open_dependency_context()
        self.files = fakefs.FakeFilesystem()
        self.fake_open = fakefs.FakeFileOpen(self.files)
        self.fake_os = fakefs.FakeOsModule(self.files)
        self.context.inject(open, self.fake_open)
        self.context.inject(os.walk, fakefs.FakeOsModule(self.files).walk)

    def tearDown(self):
        self.context.close()

    def add_file(self, filename, content):
        subdir, fn = os.path.split(filename)
        full_path = os.path.join(self.reports_path, subdir)
        full_filename = os.path.join(full_path, fn)
        self.fake_os.makedirs(full_path, exist_ok=True)
        with self.fake_open(full_filename, "w") as f:
            f.write(content)

    def add_report(self, filename, errors=0, failures=0):
        self.add_file(
            filename + ".xml",
            """
            <?xml version="1.0" encoding="UTF-8" ?>
            <testsuites>
                <testsuite name="yogurt" errors="%d" failures="%d">
                    <testcase name="spam"/>
                </testsuite>
            </testsuites>
            """
            % (errors, failures),
        )

    def exercise_sut(self):
        return junit2jenkins_status(path=self.reports_path)

    def test_success_when_no_reports(self):
        expect(self.exercise_sut()).to(equal(PASS))

    def test_success_when_only_passing_reports(self):
        self.add_report("TestSpam")
        expect(self.exercise_sut()).to(equal(PASS))

    def test_unstable_when_only_error_reports(self):
        self.add_report("TestSpam", errors=1)
        expect(self.exercise_sut()).to(equal(ERROR))

    def test_unstable_when_error_and_passing_reports(self):
        self.add_report("TestGood")
        self.add_report("TestBad", errors=1)
        expect(self.exercise_sut()).to(equal(ERROR))

    def test_failure_when_only_failing_reports(self):
        self.add_report("TestSpam", failures=1)
        expect(self.exercise_sut()).to(equal(FAIL))

    def test_failure_when_passing_and_error_and_failing_reports(self):
        self.add_report("TestUgly", errors=1)
        self.add_report("TestGood")
        self.add_report("TestBad", failures=1)
        self.add_report("TestMoUgly", errors=42)
        expect(self.exercise_sut()).to(equal(FAIL))

    def test_failure_when_report_contains_errors_and_failures(self):
        self.add_report("TestVeryBad", errors=42, failures=1)
        expect(self.exercise_sut()).to(equal(FAIL))

    def test_finds_reports_in_child_directories(self):
        self.add_report("even/deeper/TestSomething", failures=1)
        expect(self.exercise_sut()).to(equal(FAIL))

    def test_ignores_non_xml_files(self):
        self.add_file("yadda.notxml", "3rwdsfqrwefcdasrq3f")
        expect(self.exercise_sut).not_to(raise_ex(ParseError))

    def test_extension_check_is_case_insensitive(self):
        self.add_file("yadda.xMl", "3rwdsfqrwefcdasrq3f")
        expect(self.exercise_sut).to(raise_ex(ParseError))

    def test_ignores_absent_errors_attribute(self):
        self.add_file(
            "TestSpam.xml",
            """
            <?xml version="1.0" encoding="UTF-8" ?>
            <testsuites>
                <testsuite name="yogurt" failures="0">
                    <testcase name="spam"/>
                </testsuite>
            </testsuites>
            """,
        )
        expect(self.exercise_sut).not_to(raise_ex(KeyError))

    def test_ignores_absent_failures_attribute(self):
        self.add_file(
            "TestSpam.xml",
            """
            <?xml version="1.0" encoding="UTF-8" ?>
            <testsuites>
                <testsuite name="yogurt" errors="0">
                    <testcase name="spam"/>
                </testsuite>
            </testsuites>
            """,
        )
        expect(self.exercise_sut).not_to(raise_ex(KeyError))

    def test_ignores_missing_suite_element(self):
        self.add_file(
            "TestSpam.xml",
            """
            <?xml version="1.0" encoding="UTF-8" ?>
            <spam/>
            """,
        )
        expect(self.exercise_sut).not_to(raise_ex(AttributeError))

    def test_finds_suite_when_it_is_the_root_element(self):
        self.add_file(
            "TestEggs.xml",
            """
            <?xml version="1.0" encoding="UTF-8" ?>
            <testsuite name="topdog" errors="1" failures="0">
            <spam/>
            </testsuite>
            """,
        )
        expect(self.exercise_sut()).to(equal(ERROR))

    def test_finds_suite_when_it_is_the_sole_element(self):
        self.add_file(
            "TestDog.xml",
            """
            <?xml version="1.0" encoding="UTF-8" ?>
            <testsuite name="topdog" errors="1" failures="0"/>
            """,
        )
        expect(self.exercise_sut()).to(equal(ERROR))


if "__main__" == __name__:
    main()
