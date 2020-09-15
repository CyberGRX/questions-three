from copy import copy
from functools import partial
import sys
from unittest import TestCase, main

from expects import expect, be_a, equal
import yaml
from twin_sister import open_dependency_context

from twin_sister.expects_matchers import complain
import questions_three.module_cfg.loader as loader
from questions_three.module_cfg import config_for_module
from twin_sister.fakes import EmptyFake, Wrapper
from questions_three.vanilla import module_filename


YML_FILENAME = loader.YML_FILENAME


class FakeModule(EmptyFake):
    def __init__(self, *, context, name):
        self.__name__ = name
        self.__file__ = context.os.path.join("fake", "modules", name, "__init__.py")
        self._context = context
        context.create_file(self.__file__)

    def add_config(self, values):
        self._context.create_file(module_filename(self, YML_FILENAME), text=yaml.dump(values))


class TestValueTypes(TestCase):
    def setUp(self):
        loader.UNIT_TEST_MODE = True
        self.context = open_dependency_context(supply_env=True, supply_fs=True)
        self.fake_sys = Wrapper(sys)
        self.fake_sys.modules = copy(sys.modules)
        self.context.inject(sys, self.fake_sys)

    def tearDown(self):
        self.context.close()
        loader.UNIT_TEST_MODE = False

    def add_module(self, values):
        module = FakeModule(context=self.context, name="some_fake_thing")
        module.add_config(values)
        self.fake_sys.modules[module.__name__] = module
        return module.__name__

    def test_bool_false(self):
        key = "tea"
        value = False
        name = self.add_module(values={key: value})
        actual = config_for_module(name)[key]
        expect(actual).to(be_a(bool))
        expect(actual).to(equal(value))

    def test_bool_true(self):
        key = "tea"
        value = True
        name = self.add_module(values={key: value})
        actual = config_for_module(name)[key]
        expect(actual).to(be_a(bool))
        expect(actual).to(equal(value))

    def test_int(self):
        key = "darcy"
        value = 327
        name = self.add_module(values={key: value})
        actual = config_for_module(name)[key]
        expect(actual).to(be_a(int))
        expect(actual).to(equal(value))

    def test_float(self):
        key = "kmet"
        value = 94.7
        name = self.add_module(values={key: value})
        actual = config_for_module(name)[key]
        expect(actual).to(be_a(float))
        expect(actual).to(equal(value))

    def test_str(self):
        key = "ozzie"
        value = "oi"
        name = self.add_module(values={key: value})
        actual = config_for_module(name)[key]
        expect(actual).to(be_a(str))
        expect(actual).to(equal(value))

    def test_none(self):
        key = "worries"
        name = self.add_module(values={key: None})
        actual = config_for_module(name)[key]
        expect(actual).to(be_a(type(None)))

    def test_rejects_dict(self):
        name = self.add_module(values={"outer": {"inner": 42}})
        expect(partial(config_for_module, name)).to(complain(TypeError))

    def test_rejects_list(self):
        name = self.add_module(values={"menu": ["spam", "eggs", "sausage"]})
        expect(partial(config_for_module, name)).to(complain(TypeError))


if "__main__" == __name__:
    main()
