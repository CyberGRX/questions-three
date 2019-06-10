import os
import sys

from questions_three.exceptions import NoSuchRecord
from questions_three.logging import logger_for_module
from questions_three.vanilla import module_filename
import yaml
from twin_sister import dependency

from .module_cfg import ModuleCfg


# If True, use injected "open" function.
# This hack eliminates the need for unrelated unit tests to manage fake
#  module config files.
UNIT_TEST_MODE = False
VALID_TYPES = (bool, float, int, str, type(None))
YML_FILENAME = 'module_cfg.yml'


def validate_defaults(defaults, *, filename):
    for k, v in defaults.items():
        if type(v) not in VALID_TYPES:
            raise TypeError(
                '%s: %s is not in the valid types list: %s'
                % (filename, k, VALID_TYPES))


def contents_of_file(filename):
    if UNIT_TEST_MODE:
        exists = dependency(os.path).exists
        fopen = dependency(open)
    else:
        exists = os.path.exists
        fopen = open
    if exists(filename):
        with fopen(filename, 'r') as f:
            return f.read()
    return ''


def parent_module(module):
    parts = module.__name__.split('.')
    if len(parts) > 1:
        name = '.'.join(parts[:-1])
        return dependency(sys).modules[name]
    return None


def inherit_missing_defaults(*, defaults, parent_module):
    return dict(defaults_for_module(parent_module), **defaults)


def defaults_for_module(module):
    log = logger_for_module(__name__)
    filename = module_filename(module, YML_FILENAME)
    defaults = yaml.load(contents_of_file(filename), Loader=yaml.Loader) or {}
    log.debug('Configuration from %s: %s' % (filename, defaults))
    validate_defaults(defaults, filename=filename)
    parent = parent_module(module)
    if parent:
        defaults = inherit_missing_defaults(
            defaults=defaults, parent_module=parent)
    return defaults


def config_for_module(module_name):
    modules = dependency(sys).modules
    if module_name not in modules.keys():
        raise NoSuchRecord('Found no module called "%s"' % module_name)
    return ModuleCfg(
        defaults=defaults_for_module(modules[module_name]),
        module_name=module_name)
