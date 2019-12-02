#!/usr/bin/env python

import os
from setuptools import find_packages, setup
from setuptools.command.test import test
from unittest import TestLoader
from unittest.runner import TextTestRunner

MAJOR_VERSION = int(os.environ.get('QUESTIONS_THREE_MAJOR_VERSION', 0))
MINOR_VERSION = int(os.environ.get('QUESTIONS_THREE_MINOR_VERSION', 0))
PATCH_VERSION = int(os.environ.get('QUESTIONS_THREE_PATCH_VERSION', 0))


class Tester(test):

    def run_tests(self):
        tests = TestLoader().discover('tests', pattern='test_*.py')
        runner = TextTestRunner()
        result = runner.run(tests)
        exit(0 if result.wasSuccessful() else 1)


def build_number():
    if 'BUILD_NUMBER' in os.environ.keys():
        return int(os.environ['BUILD_NUMBER'])
    return 0


setup(
    name='questions-three-selenium',
    version='%d.%d.%d.%d' % (
        MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION, build_number()),
    description='Selenium integration and tools for questions-three',
    author='Mike Duskis',
    author_email='mike.duskis@cybergrx.com',
    packages=find_packages(exclude=('tests.*', 'tests')),
    url='https://git.dev.grx.io/Testing/questions-three',
    install_requires=[
        'expects>=0.8.0',  # required by unit tests
        'questions-three',
        'pyfakefs>=3.4.3',  # required by unit tests
        'PyYAML>=5.1',  # required by ModuleConfig
        'selenium>=3.141.0',
        'twin-sister>=4.5.1',  # required by unit tests
        'twine>=1.9.1',  # required by setup to upload package to Nexus
        'wheel>=0.30.0'  # required by setup to build package
        ],
    cmdclass={'test': Tester},
    package_data={
        'questions_three_selenium': ['module_cfg.yml'],
        'questions_three_selenium.dom_dumper': ['dump_dom.js']
        })
