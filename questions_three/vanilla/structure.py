from collections.abc import Mapping
import json
from random import randrange
import sys


def flatten(obj):
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    if isinstance(obj, list):
        return [flatten(x) for x in obj]
    return obj


def to_json_serializable(obj):
    if obj is None:
        return obj
    if hasattr(obj, 'items'):
        return {k: to_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_json_serializable(i) for i in obj]
    if type(obj) in (int, float, complex):
        return obj
    return(str(obj))


class Structure(Mapping):
    """
    Structure of nested key/value pairs, accessible as attributes.
    """

    @classmethod
    def from_json(cls, json_string):
        return cls(**json.loads(json_string))

    @classmethod
    def _inflate_if_mapping(cls, obj):
        if isinstance(obj, list):
            return [cls._inflate_if_mapping(o) for o in obj]
        if {'keys', 'values', 'items'} <= set(dir(obj)):
            return cls(**obj)
        return obj

    def __init__(self, **kwargs):
        self._hash = randrange(sys.maxsize)
        self._members = {
            k: self._inflate_if_mapping(v)
            for k, v in kwargs.items()}

    def __getattr__(self, name):
        if name in self._members.keys():
            return self._members[name]
        raise AttributeError('I have no "%s"' % name)

    def __eq__(self, other):
        if not hasattr(other, 'keys'):
            return False
        my_keys = self.keys()
        other_keys = other.keys()
        return(
            len(my_keys) == len(other_keys) and
            all([k in other_keys for k in my_keys]) and
            all([self[k] == other[k] for k in my_keys])
        )

    def __hash__(self):
        return self._hash

    def __iter__(self):
        return iter(self._members)

    def __getitem__(self, name):
        return self._members[name]

    def __len__(self):
        return len(self._members)

    def __repr__(self):
        return 'Structure: %s' % self.to_dict()

    def __setattr__(self, key, value):
        if key.startswith('_'):
            self.__dict__[key] = value
        else:
            self._members[key] = value

    def __setitem__(self, key, value):
        self._members[key] = value

    def _child_structures(self):
        return [
            val for val in self.values()
            if isinstance(val, self.__class__)]

    def find(self, key):
        if key in self.keys():
            return getattr(self, key)
        for child in self._child_structures():
            val = child.find(key)
            if val:
                return val
        return None

    def items(self):
        return self._members.items()

    def keys(self):
        return self._members.keys()

    def to_dict(self):
        return {
            k: flatten(v)
            for k, v in self.items()}

    def to_json(self):
        try:
            return json.dumps(
                {
                    k: to_json_serializable(v)
                    for k, v in self.to_dict().items()})
        except TypeError as e:
            raise TypeError('%s\n%s' % (e, repr(self))) from e

    def values(self):
        return self._members.values()
