import os

from twin_sister import dependency

from questions_three.exceptions import InvalidConfiguration

from .transform_type import transform_type


class ModuleCfg:

    def __init__(self, defaults, *, module_name='unidentified module'):
        self._defaults = {k.lower(): v for k, v in defaults.items()}
        self._env = dependency(os).environ
        self._module_name = module_name

    def _from_env(self, name):
        lc_name = name.lower()
        matches = [v for k, v in self._env.items() if lc_name == k.lower()]
        count = len(matches)
        if 0 == count:
            return None
        if 1 == count:
            return matches[0]
        raise InvalidConfiguration(
            'Found more than one environment variable that could '
            'match "%s" (case insensitive)' % name)

    def __getitem__(self, name):
        lc_name = name.lower()
        if lc_name not in self._defaults.keys():
            raise InvalidConfiguration(
                'Refusing to use "%s" from the environment '
                'because it was not defined in a module configuration file '
                'for %s'
                % (name, self._module_name))
        default = self._defaults[lc_name]
        from_env = self._from_env(name)
        return default if from_env is None else transform_type(
            key=name, val=from_env, new_type=type(default))

    def to_dict(self):
        return {
            name: self[name]
            for name in self._defaults.keys()}

    __getattr__ = __getitem__
