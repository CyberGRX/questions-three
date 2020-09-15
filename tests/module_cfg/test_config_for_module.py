from copy import copy
from functools import partial
import sys
from unittest import TestCase, main
import yaml

from expects import expect, be_a, equal

from questions_three.exceptions import NoSuchRecord
from twin_sister.expects_matchers import complain
from questions_three.module_cfg import config_for_module
import questions_three.module_cfg.loader as loader
from questions_three.module_cfg.module_cfg import ModuleCfg
from twin_sister.fakes import EmptyFake, Wrapper
from questions_three.vanilla import module_filename
from twin_sister import open_dependency_context


YML_FILENAME = loader.YML_FILENAME


class FakeModule(EmptyFake):
    def __init__(self, *, context, name):
        self.__name__ = name
        self.__file__ = context.os.path.join("fake", "modules", name, "__init__.py")
        self._context = context
        context.create_file(self.__file__)

    def add_config(self, values):
        self._context.create_file(module_filename(self, YML_FILENAME), text=yaml.dump(values))


class TestConfigForModule(TestCase):
    def setUp(self):
        loader.UNIT_TEST_MODE = True
        self.context = open_dependency_context(supply_env=True, supply_fs=True)
        self.fake_sys = Wrapper(sys)
        self.fake_sys.modules = copy(sys.modules)
        self.context.inject(sys, self.fake_sys)

    def tearDown(self):
        self.context.close()
        loader.UNIT_TEST_MODE = False

    def load_module(self, module):
        self.fake_sys.modules[module.__name__] = module

    def test_finds_config_file(self):
        key = "indicator"
        value = "squawk!"
        module_name = "parrot"
        module = FakeModule(context=self.context, name=module_name)
        module.add_config({key: value})
        self.load_module(module)
        config = config_for_module(module_name)
        expect(config).to(be_a(ModuleCfg))
        expect(config[key]).to(equal(value))

    def test_returns_empty_instance_when_module_has_no_config(self):
        module_name = "has_no_config"
        module = FakeModule(context=self.context, name=module_name)
        self.load_module(module)
        config = config_for_module(module_name)
        expect(config).to(be_a(ModuleCfg))

    def test_complains_when_module_not_found(self):
        expect(partial(config_for_module, "no_esta")).to(complain(NoSuchRecord))


if "__main__" == __name__:
    main()
