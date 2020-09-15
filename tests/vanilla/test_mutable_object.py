from unittest import TestCase, main

from expects import expect, equal, raise_error

from questions_three.vanilla import MutableObject


class TestMutableObject(TestCase):
    def test_object_is_mutable(self):
        thing = MutableObject()
        name = "ximinez"
        value = 77

        def attempt():
            setattr(thing, name, value)

        expect(attempt).not_to(raise_error(AttributeError))
        expect(getattr(thing, name)).to(equal(value))


if "__main__" == __name__:
    main()
