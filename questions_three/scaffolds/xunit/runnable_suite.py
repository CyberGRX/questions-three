def bind_attributes(obj, attrs):
    for k, v in attrs.items():
        if not isinstance(v, type) and '__call__' in dir(v):
            bind_method(obj, k, v)
        else:
            setattr(obj, k, v)


def bind_method(obj, name, func):
    setattr(obj, name, func.__get__(obj, obj.__class__))


class RunnableSuite:

    def __init__(self, attrs):
        self.__dict__['_suite_context'] = {}
        bind_attributes(self, attrs)

    def __getattr__(self, name):
        if name in self._suite_context.keys():
            return self._suite_context[name]
        if name in ['setup', 'setup_suite', 'teardown', 'teardown_suite']:
            # Default setup and teardown methods.
            # We can't define these with the typical "def" construct
            # because this would supercede __getattr__ and prevent
            # child classes from overriding these methods.
            return lambda: None
        raise AttributeError('I have no "%s"' % name)

    def __setattr__(self, name, value):
        self._suite_context[name] = value

    def get_suite_context(self):
        return self._suite_context

    def run_one_test(self, test_name):
        self.setup()
        try:
            getattr(self, test_name)()
        finally:
            self.teardown()
