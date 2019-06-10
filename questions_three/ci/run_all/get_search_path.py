import sys

from twin_sister import dependency

from questions_three.module_cfg import config_for_module


def get_search_path():
    argv = dependency(sys.argv)
    if len(argv) > 1:
        return argv[1]
    return config_for_module(__name__).path_to_tests
