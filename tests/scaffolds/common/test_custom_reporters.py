from contextlib import contextmanager
import importlib
from io import StringIO
from unittest import TestCase, main

from expects import expect, equal
from twin_sister import open_dependency_context

from questions_three.exceptions import InvalidConfiguration
from twin_sister.expects_matchers import raise_ex
from questions_three.scaffolds.common.activate_reporters import activate_reporters
from twin_sister.fakes import EmptyFake


class FakeImportLib:
    def __init__(self):
        self._modules = {}

    def add_module(self, name, module):
        self._modules[name] = module

    def import_module(self, name, package=None):
        if name in self._modules:
            return self._modules[name]
        return importlib.import_module(name, package)

    def __getattr__(self, name):
        return getattr(importlib, name)


class FakeFiles(EmptyFake):
    def __init__(self):
        self._files = {}

    def create(self, filename, content):
        self._files[filename] = content

    @contextmanager
    def open(self, filename, mode):
        if filename in self._files.keys():
            expect(mode).to(equal("r"))
            f = StringIO(self._files[filename])
        else:
            f = open(filename, mode)
        yield f
        f.close()


class HandlerSpy:
    def __init__(self):
        self.was_activated = False

    def __call__(self):
        return self

    def activate(self):
        self.was_activated = True


class TestCustomReporters(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True)
        self.fake_importer = FakeImportLib()
        self.context.inject(importlib, self.fake_importer)
        self.fake_files = FakeFiles()
        self.context.inject(open, self.fake_files.open)

    def tearDown(self):
        self.context.close()

    def set_filename(self, name):
        self.context.os.environ["CUSTOM_REPORTERS_FILE"] = name

    def test_ignores_comment_line(self):
        reporters_filename = "/here/is/something/silly"
        self.set_filename(reporters_filename)
        module_name = "fake_module"
        self.fake_importer.add_module(module_name, EmptyFake())
        self.fake_files.create(
            reporters_filename,
            """
            # This should be ignored
            %s.FakeClass
            # This should be ignored too
            """
            % module_name,
        )
        expect(activate_reporters).not_to(raise_ex(Exception))

    def test_activates_specified_class(self):
        reporters_filename = "/here/is/something/silly"
        self.set_filename(reporters_filename)
        module_name = "fake_module"
        class_name = "FakeClass"
        module = EmptyFake()
        spy = HandlerSpy()
        setattr(module, class_name, spy)
        self.fake_importer.add_module(module_name, module)
        self.fake_files.create(
            reporters_filename,
            """
            %s.%s
            """
            % (module_name, class_name),
        )
        activate_reporters()
        assert spy.was_activated, "Handler was not activated"

    def test_ignores_empty_line(self):
        reporters_filename = "/here/is/something/silly"
        self.set_filename(reporters_filename)
        module_name = "fake_module"
        self.fake_importer.add_module(module_name, EmptyFake())
        self.fake_files.create(
            reporters_filename,
            """

            %s.FakeClass

            """
            % module_name,
        )
        expect(activate_reporters).not_to(raise_ex(Exception))

    def test_complains_when_cannot_parse_line(self):
        reporters_filename = "/here/is/something/silly"
        self.set_filename(reporters_filename)
        module_name = "fake_module"
        self.fake_importer.add_module(module_name, EmptyFake())
        self.fake_files.create(
            reporters_filename,
            """
            Stop being silly
            """,
        )
        expect(activate_reporters).to(raise_ex(InvalidConfiguration))


if "__main__" == __name__:
    main()
