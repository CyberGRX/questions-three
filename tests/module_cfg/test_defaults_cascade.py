from copy import copy
import sys
from unittest import TestCase, main

from expects import expect, equal
import yaml
from twin_sister import open_dependency_context

import questions_three.module_cfg.loader as loader
from twin_sister.fakes import EmptyFake, Wrapper
from questions_three.vanilla import module_filename

YML_FILENAME = loader.YML_FILENAME
config_for_module = loader.config_for_module


class FakeModule(EmptyFake):

    def __init__(self, *, context, name):
        self.__name__ = name
        self.__file__ = context.os.path.join(
            'fake', 'modules', name, '__init__.py')
        self._context = context
        context.create_file(self.__file__)

    def __bool__(self):
        return True

    def add_config(self, values):
        self._context.create_file(
            module_filename(self, YML_FILENAME),
            text=yaml.dump(values))


class TestDefaultsCascade(TestCase):

    def setUp(self):
        loader.UNIT_TEST_MODE = True
        self.context = open_dependency_context(supply_env=True, supply_fs=True)
        self.fake_sys = Wrapper(sys)
        self.fake_sys.modules = copy(sys.modules)
        self.context.inject(sys, self.fake_sys)

    def tearDown(self):
        self.context.close()
        loader.UNIT_TEST_MODE = False

    def add_module(self, name, values):
        module = FakeModule(context=self.context, name=name)
        module.add_config(values)
        self.fake_sys.modules[module.__name__] = module
        return module.__name__

    def test_uses_parent_value_when_child_has_none(self):
        key = 'the_answer'
        value = 42
        parent_name = 'fake'
        child_name = parent_name + '.child'
        self.add_module(parent_name, {key: value})
        self.add_module(child_name, {'something_else': 'spinach'})
        expect(config_for_module(child_name)[key]).to(
            equal(value))

    def test_uses_grandparent_value_when_parent_has_none(self):
        key = 'the_question'
        value = 'eight sixes'
        gp_name = 'one'
        self.add_module(gp_name, {key: value})
        p_name = '.'.join((gp_name, 'two'))
        self.add_module(p_name, {'something': 'else'})
        child_name = '.'.join((p_name, 'three'))
        self.add_module(child_name, {})
        expect(config_for_module(child_name)[key]).to(
            equal(value))

    def test_parent_overrides_grandparent(self):
        key = 'a_conflict'
        parent_value = 'value from parent'
        gp_value = 'value from grandparent'
        gp_name = 'grandparent'
        self.add_module(gp_name, {key: gp_value})
        parent_name = '.'.join((gp_name, 'parent'))
        self.add_module(parent_name, {key: parent_value})
        child_name = '.'.join((parent_name, 'child'))
        self.add_module(child_name, {})
        expect(config_for_module(child_name)[key]).to(
            equal(parent_value))

    def test_child_overrides_parent(self):
        key = 'a_conflict'
        parent_value = 'value from parent'
        child_value = 'value from child'
        parent_name = 'parent'
        self.add_module(parent_name, {key: parent_value})
        child_name = '.'.join((parent_name, 'child'))
        self.add_module(child_name, {key: child_value})
        expect(config_for_module(child_name)[key]).to(
            equal(child_value))

    def test_child_can_override_parent_with_none(self):
        key = 'a_conflict'
        parent_value = 'value from parent'
        child_value = None
        parent_name = 'parent'
        self.add_module(parent_name, {key: parent_value})
        child_name = '.'.join((parent_name, 'child'))
        self.add_module(child_name, {key: child_value})
        expect(config_for_module(child_name)[key]).to(
            equal(child_value))

    def test_override_is_case_insensitive(self):
        parent_key = 'ThInG'
        parent_value = 'value from parent'
        child_key = 'tHiNg'
        child_value = 'value from child'
        parent_name = 'parent'
        self.add_module(parent_name, {parent_key: parent_value})
        child_name = '.'.join((parent_name, 'child'))
        self.add_module(child_name, {child_key: child_value})
        expect(config_for_module(child_name)[parent_key]).to(
            equal(child_value))


if '__main__' == __name__:
    main()
