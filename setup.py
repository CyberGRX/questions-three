#!/usr/bin/env python

import os
from setuptools import find_packages, setup
from setuptools.command.test import test
from unittest import TestLoader
from unittest.runner import TextTestRunner

MAJOR_VERSION = 3
# An even MINOR_VERSION number indicates a public release
MINOR_VERSION = 14
PATCH_VERSION = 2


class Tester(test):
    def run_tests(self):
        tests = TestLoader().discover("tests", pattern="test_*.py")
        runner = TextTestRunner()
        result = runner.run(tests)
        exit(0 if result.wasSuccessful() else 1)


def build_number():
    if "BUILD_NUMBER" in os.environ.keys():
        return int(os.environ["BUILD_NUMBER"])
    return 0


def requirements(f):
    with open(f) as fd:
        return [
            l for l in [r.strip() for r in fd.readlines()] if l and not l.startswith("-") and not l.startswith("#")
        ]


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    author="Mike Duskis",
    author_email="mike.duskis@cybergrx.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Testing",
    ],
    cmdclass={"test": Tester},
    description="Toolkit for building automated integration checks",
    install_requires=requirements("requirements.txt"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="questions-three",
    package_data={
        "questions_three": ["module_cfg.yml"],
        "questions_three.webdriver_tools.dom_dumper": ["dump_dom.js"],
    },
    packages=find_packages(exclude=("tests.*", "tests")),
    url="https://github.com/CyberGRX/questions-three",
    version="%d.%d.%d.%d" % (MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION, build_number()),
)
