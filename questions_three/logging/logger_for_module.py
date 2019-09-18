import logging
from logging import Formatter, INFO, Logger
import os

from twin_sister import dependency

from .constants import MESSAGE_FORMAT


def _parent_module_name(module_name):
    parts = module_name.split('.')
    if len(parts) > 1:
        return '.'.join(parts[:-1])
    return None


def _level_for_module(module_name, environ):
    var_name = '%s_LOG_LEVEL' % module_name.replace('.', '_').upper()
    if var_name in environ.keys():
        level = getattr(logging, environ[var_name])
    else:
        parent_module = _parent_module_name(module_name)
        if parent_module:
            level = _level_for_module(parent_module, environ=environ)
        else:
            level = INFO
    return level


def logger_for_module(module_name):
    """
    Return a Logger for the module with the given name.
    Its level can be controlled by an environment variable:
      <module_name.upper()>_LOG_LEVEL=<DEBUG | INFO | WARNING | ERROR>

    module_name -- (str)  Name of the module
    """
    environ = dependency(os).environ
    handler = dependency(logging).StreamHandler()
    handler.setFormatter(Formatter(fmt=MESSAGE_FORMAT))
    logger = Logger(name=module_name)
    logger.addHandler(handler)
    logger.setLevel(_level_for_module(module_name, environ=environ))
    return logger
