from functools import partial
import json
from unittest import TestCase, main

from expects import expect, equal

from twin_sister.expects_matchers import raise_ex
from questions_three.vanilla import Structure, structures_from_json, structures_to_json


class TestListOfStructures(TestCase):
    def test_to_json_produces_json(self):

        serialized = structures_to_json((Structure(yankees=7, mets=2),))
        expect(partial(json.loads, serialized)).not_to(raise_ex(Exception))

    def test_to_and_from_json(self):
        original = [Structure(spam=Structure(eggs=1, sausage=["spam"])), Structure(larry=1, moe=3, curly=0)]
        expect(structures_from_json(structures_to_json(original))).to(equal(original))


if "__main__" == __name__:
    main()
