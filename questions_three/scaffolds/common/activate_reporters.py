import importlib
import re

from twin_sister import dependency

from questions_three.exceptions import InvalidConfiguration
from questions_three.module_cfg import config_for_module
from questions_three.reporters.artifact_saver import ArtifactSaver
from questions_three.reporters.event_logger import EventLogger
from questions_three.reporters.junit_reporter import JunitReporter
from questions_three.reporters.result_compiler import ResultCompiler


BUILT_IN_REPORTERS = (
    ArtifactSaver, EventLogger, JunitReporter, ResultCompiler)

_active_reporters = []

enabled = True


def custom_reporter_filename():
    conf = config_for_module(__name__)
    return conf.custom_reporters_file


def custom_reporter_class_names():
    filename = custom_reporter_filename()
    if filename:
        with dependency(open)(filename, 'r') as f:
            return [
                line
                for line in [l.strip() for l in f.read().split('\n')]
                if line and not line.startswith('#')]
    return []


MODULE_AND_CLASS_PATTERN = re.compile(r'^(.*?)\.([^\.]+)$')


def import_class(full_name):
    mat = MODULE_AND_CLASS_PATTERN.match(full_name)
    if not mat:
        raise InvalidConfiguration(
            'Failed to parse line in %s: "%s"'
            % (custom_reporter_filename(), full_name))
    module_name, class_name = mat.groups()
    module = dependency(importlib).import_module(module_name)
    return getattr(module, class_name)


def configured_reporters():
    conf = config_for_module(__name__)
    configured_names = conf.event_reporters.split(',')
    return [
        cls for cls in BUILT_IN_REPORTERS
        if cls.__name__ in configured_names
    ]


def custom_reporters():
    return [import_class(name) for name in custom_reporter_class_names()]


def activate_reporters():
    if not enabled:
        return
    for cls in configured_reporters() + custom_reporters():
        reporter = cls()
        reporter.activate()
        # Create a strong reference so the subscriber stays alive
        _active_reporters.append(reporter)
