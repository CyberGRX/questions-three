#!/usr/bin/env python

import os
from setuptools import find_packages, setup
from setuptools.command.test import test
from unittest import TestLoader
from unittest.runner import TextTestRunner

MAJOR_VERSION = 2
# An even MINOR_VERSION number indicates a public release
MINOR_VERSION = 6
PATCH_VERSION = 1


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
    name='questions-three',
    version='%d.%d.%d.%d' % (
        MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION, build_number()),
    description='Fundamental components of an automated test platform',
    author='Mike Duskis',
    author_email='mike.duskis@cybergrx.com',
    packages=find_packages(exclude=('tests.*', 'tests')),
    url='https://github.com/CyberGRX/questions-three',
    install_requires=[
        'boto3>=1.9.146',  # required to save artifacts to s3
        'expects>=0.8.0',  # required by unit tests
        'pyfakefs>=3.4.3',  # required by unit tests
        'PyYAML>=5.1',  # required by ModuleConfig
        'junit-xml>=1.8',  # required by junit reporter
        'lxml>=4.1.1',  # required by html_form
        'requests>=2.18.4',  # required by HTTP Client
        'twin-sister>=4.2.6.0',  # required by unit tests
        'twine>=1.9.1',  # required by setup to upload package to Nexus
        'wheel>=0.30.0'  # required by setup to build package
        ],
    cmdclass={'test': Tester},
    package_data={
        'questions_three': ['module_cfg.yml'],
        'questions_three.webdriver_tools.dom_dumper': ['dump_dom.js']
        })
