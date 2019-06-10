import json

from .structure import Structure


def structures_from_json(json_string):
    return [Structure(**dct) for dct in json.loads(json_string)]


def structures_to_json(sequence_of_structures):
    return '[' + ','.join([s.to_json() for s in sequence_of_structures]) + ']'
