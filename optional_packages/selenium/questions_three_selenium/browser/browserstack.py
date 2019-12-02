from datetime import datetime, timedelta
from urllib.parse import quote_plus, urlsplit, urlunsplit

from questions_three.exceptions import InvalidConfiguration
from questions_three.module_cfg import config_for_module
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from twin_sister import dependency

from ..browser_stack_tunnel import BrowserStackTunnel
from ..exceptions import AllBrowsersBusy

from .require_browserstack_tunnel import require_browserstack_tunnel


def str2bool(s):
    return s and 'true' == s.lower()


def prepend_bs_credentials(netloc):
    config = config_for_module(__name__)
    return '%s:%s@%s' % (
        quote_plus(config.browserstack_username),
        quote_plus(config.browserstack_access_key),
        netloc)


def insert_bs_credentials(url):
    scheme, netloc, path, query, fragment = urlsplit(url)
    return urlunsplit((
        scheme, prepend_bs_credentials(netloc=netloc),
        path, query, fragment))


def now():
    return dependency(datetime).now()


def launch_browserstack_browser():
    config = config_for_module(__name__)
    for name in ('browserstack_access_key', 'browserstack_username'):
        if not config[name]:
            raise InvalidConfiguration(
                '"%s" is not in the environment or a configuration file'
                % name)
    if require_browserstack_tunnel():
        tunnel = dependency(BrowserStackTunnel)()
    else:
        tunnel = None
    caps = {
            'browser': config.use_browser,
            'browserstack.debug': config.browserstack_set_debug,
            'browserstack.local': config.browserstack_set_local,
            'resolution': config.browserstack_screen_resolution,
            'os': config.browserstack_os,
            'os_version': config.browserstack_os_version}
    browser_version = config.use_browser_version
    if browser_version:
        caps['browser_version'] = browser_version
    if tunnel is not None:
        caps['browserstack.localIdentifier'] = tunnel.local_identifier
    start = now()
    expiry = start + timedelta(seconds=config.browserstack_tunnel_timeout)
    while True:
        try:
            remote = dependency(webdriver).Remote(
                command_executor=insert_bs_credentials(
                    url=config.browserstack_url),
                desired_capabilities=caps)
            break
        except WebDriverException as e:
            msg = str(e).lower()
            if 'all parallel tests are currently in use' in msg:
                raise AllBrowsersBusy(msg)
            if 'browserstack.local' in msg and now() <= expiry:
                continue
            raise
    remote.fullscreen_window()
    return remote
