from questions_three.module_cfg import config_for_module
from questions_three.vanilla import call_with_exception_tolerance
from selenium import webdriver
from twin_sister import dependency

from ..exceptions import AllBrowsersBusy, UnsupportedBrowser

from .browserstack import launch_browserstack_browser
from .selenium_grid import launch_selenium_grid_browser


def launch_chrome():
    config = config_for_module(__name__)
    opts = dependency(webdriver.chrome.options.Options)()
    opts.add_argument('start-fullscreen')
    agent_string = config.chrome_user_agent
    if agent_string:
        opts.add_argument('user-agent=%s' % agent_string)
    return dependency(webdriver).Chrome(
        chrome_options=opts)


def launch_firefox():
    return dependency(webdriver).Firefox()


def launch_local_browser():
    config = config_for_module(__name__)
    browser_name = config.use_browser
    if browser_name:
        browser_name = browser_name.lower()
    if browser_name in ('chrome', None):
        return launch_chrome()
    if 'firefox' == browser_name:
        return launch_firefox()
    raise UnsupportedBrowser('"%s" is not supported' % browser_name)


def get_launch_function():
    config = config_for_module(__name__)
    location = config.browser_location
    if location:
        location = location.lower()
    if 'browserstack' == location:
        return launch_browserstack_browser
    if 'selenium_grid' == location:
        return launch_selenium_grid_browser
    return launch_local_browser


def launch_browser():
    config = config_for_module(__name__)
    launch = get_launch_function()
    return call_with_exception_tolerance(
        func=launch,
        tolerate=AllBrowsersBusy,
        timeout=config.browser_availability_timeout,
        throttle=config.browser_availability_throttle)
