class AllBrowsersBusy(RuntimeError):
    pass


class BrowserStackTunnelClosed(RuntimeError):
    pass


class TooManyElements(RuntimeError):
    pass


class UnknownSelector(RuntimeError):
    pass


class UnsupportedBrowser(RuntimeError):
    pass
