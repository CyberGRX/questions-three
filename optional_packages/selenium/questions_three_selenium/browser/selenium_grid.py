from questions_three.exceptions import InvalidConfiguration
from questions_three.module_cfg import config_for_module
from twin_sister import dependency
from selenium import webdriver


def launch_selenium_grid_browser():
    config = config_for_module(__name__)
    hub_url = config.selenium_grid_hub_url
    if not hub_url:
        raise InvalidConfiguration(
            'Expected $SELENIUM_GRID_HUB_URL to be configured.')
    caps = {
        'browserName': config.use_browser}
    if config.use_browser:
        caps['browserName'] = config.use_browser
    browser_version = config.use_browser_version
    if browser_version:
        caps['version'] = browser_version
    return dependency(webdriver).Remote(
        command_executor=hub_url,
        desired_capabilities=caps)
