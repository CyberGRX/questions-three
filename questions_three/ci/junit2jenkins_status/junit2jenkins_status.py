import os
from xml.etree import ElementTree

from twin_sister import dependency

from .status import ERROR, FAIL, PASS


def locate_suite(root):
    return root if 'testsuite' == root.tag \
        else root.find(".//testsuite")


def extract_status(filename):
    with dependency(open)(filename, 'r') as f:
        xml = f.read().strip()
    root = ElementTree.fromstring(xml)
    suite = locate_suite(root)
    if suite is not None:
        keys = suite.attrib.keys()
        if 'failures' in keys and int(suite.attrib['failures']):
            return FAIL
        if 'errors' in keys and int(suite.attrib['errors']):
            return ERROR
    return PASS


def walk(path):
    return dependency(os.walk)(path)


def junit2jenkins_status(*, path):
    erred = False
    for dirpath, dirnames, filenames in walk(path):
        for fn in filenames:
            if not fn.lower().endswith('.xml'):
                continue
            status = extract_status(os.path.join(dirpath, fn))
            if ERROR == status:
                # We still need to look for failures
                erred = True
            if FAIL == status:
                # One failure fails the whole lot
                return FAIL
    return ERROR if erred else PASS
