This test module is called "loggin" rather  than "logging" because unittest objects:

======================================================================
ERROR: logging.test_logger_for_module (unittest.loader._FailedTest)
----------------------------------------------------------------------
ImportError: Failed to import test module: logging.test_logger_for_module
Traceback (most recent call last):
  File "/Users/mike.duskis/.pyenv/versions/3.6.4/lib/python3.6/unittest/loader.py", line 428, in _find_test_path
    module = self._get_module_from_name(name)
  File "/Users/mike.duskis/.pyenv/versions/3.6.4/lib/python3.6/unittest/loader.py", line 369, in _get_module_from_name
    __import__(name)
ModuleNotFoundError: No module named 'logging.test_logger_for_module'


----------------------------------------------------------------------
