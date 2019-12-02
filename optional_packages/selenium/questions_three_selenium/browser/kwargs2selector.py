from selenium.webdriver.common.by import By

from ..exceptions import UnknownSelector


BY_CONSTANTS = {
    name.lower(): getattr(By, name)
    for name in dir(By)
    if not name.startswith('_')}


def kwargs2selector(**kwargs):
    """
    Given "by=selector" somewhere in kwargs,
    return (By.constant, selector) suitable for passing to find_elements()
    """
    for name, value in kwargs.items():
        if 'qa_id' == name:
            return By.XPATH, "//*[@data-qa='%s']" % value
        if name in BY_CONSTANTS.keys():
            return BY_CONSTANTS[name], value
    raise UnknownSelector('Found no known "by" selector in %s' % kwargs)
