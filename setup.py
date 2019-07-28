#!/usr/bin/env python

import os
from setuptools import find_packages, setup
from setuptools.command.test import test
from unittest import TestLoader
from unittest.runner import TextTestRunner

MAJOR_VERSION = 2
# An even MINOR_VERSION number indicates a public release
MINOR_VERSION = 6
PATCH_VERSION = 3


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
    author='Mike Duskis',
    author_email='mike.duskis@cybergrx.com',
    cmdclass={'test': Tester},
    description='Fundamental components of an automated test platform',
    install_requires=[
        'boto3==1.9.192',  # required to save artifacts to s3
        'botocore==1.12.192', # temporarily fixed the version of this and boto3 to work around https://github.com/boto/botocore/issues/1789
        'expects>=0.8.0',  # required by unit tests
        'junit-xml>=1.8',  # required by junit reporter
        'lxml>=4.1.1',  # required by html_form
        'PyYAML>=5.1',  # required by ModuleConfig
        'pyfakefs>=3.4.3',  # required by unit tests
        'requests>=2.18.4',  # required by HTTP Client
        'twin-sister>=4.2.6.0',  # required by unit tests
        'twine>=1.9.1',  # required by setup to upload package to Nexus
        'wheel>=0.30.0'  # required by setup to build package
        ],
    name='questions-three',
    package_data={
        'questions_three': ['module_cfg.yml'],
        'questions_three.webdriver_tools.dom_dumper': ['dump_dom.js']
        },
    packages=find_packages(exclude=('tests.*', 'tests')),
    url='https://github.com/CyberGRX/questions-three',
    version='%d.%d.%d.%d' % (
        MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION, build_number()),
        )
