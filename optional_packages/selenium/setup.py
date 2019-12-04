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


with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    author='Mike Duskis',
    author_email='mike.duskis@cybergrx.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing'],
    cmdclass={'test': Tester},
    description='Selenium integration and tools for questions-three',
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
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='questions-three-selenium',
    package_data={
        'questions_three_selenium': ['module_cfg.yml'],
        'questions_three_selenium.dom_dumper': ['dump_dom.js']},
    packages=find_packages(exclude=('tests.*', 'tests')),
    version='%d.%d.%d.%d' % (
        MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION, build_number()),
    url='https://github.com/CyberGRX/questions-three'
    )
