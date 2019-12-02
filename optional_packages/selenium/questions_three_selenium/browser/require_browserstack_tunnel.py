from questions_three.module_cfg import config_for_module


def require_browserstack_tunnel():
    conf = config_for_module(__name__)
    return (
        'BrowserStack' == conf.browser_location and
        conf.browserstack_set_local)
