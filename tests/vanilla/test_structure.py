import json
from unittest import TestCase, main

from expects import expect, be_a, equal

from twin_sister.expects_matchers import contain_key_with_value, raise_ex
from questions_three.vanilla import Structure


ARBITRARY_DICT = {
            'things': [1, 2, 3],
            'stuffs': {'part1': [5, 6], 'part2': 'The Spinach Imposition'}}


class TestStructure(TestCase):

    def test_returns_level_one(self):
        spam_count = 42
        sut = Structure(spams=spam_count, eggs=1)
        expect(sut.spams).to(equal(spam_count))

    def test_returns_level_three(self):
        spam_count = 0x42
        things = {
            'one': {
                'two': {
                    'spams': spam_count}}}
        sut = Structure(**things)
        expect(sut.one.two.spams).to(equal(spam_count))

    def test_raises_attribute_error(self):
        sut = Structure(apples=2, oranges=3)

        def attempt():
            sut.bananas

        expect(attempt).to(raise_ex(AttributeError))

    def test_finds_key_three_levels_down(self):
        sut = Structure(one={'two': {'three': 'spam'}})
        expect(sut.find('three')).to(equal('spam'))

    def test_does_not_find_non_existent_key(self):
        expect(Structure(one='biggles').find('two')).to(equal(None))

    def test_finds_value_in_nested_structure(self):
        sut = Structure(one=Structure(target='spam'))
        expect(sut.find('target')).to(equal('spam'))

    def test_returns_value_as_dict_item(self):
        key = 'number_37'
        value = 'the larch'
        sut = Structure(**{key: value, 'not_the_key': 'wrong'})
        expect(sut[key]).to(equal(value))

    def test_raises_key_error_when_dict_item_does_not_match_attribute(self):
        sut = Structure(spams=200)

        def attempt():
            sut['beans']

        expect(attempt).to(raise_ex(KeyError))

    def test_can_retrieve_keys_as_sequence(self):
        sut = Structure(key1='a', key2='b', key3='c')
        keys = sut.keys()
        assert hasattr(keys, '__iter__'), \
            'keys() returned a %s. Expected a sequence type' % type(keys)
        expect(set(keys)).to(equal({'key1', 'key2', 'key3'}))

    def test_can_retrieve_values_as_sequence(self):
        sut = Structure(a='spam', b='eggs', c='sausage')
        values = sut.values()
        assert hasattr(values, '__iter__'), \
            'values() returned a %s.  Expected a sequence type' % type(values)
        expect(set(values)).to(equal({'spam', 'eggs', 'sausage'}))

    def test_test_can_retrieve_items_as_sequence_of_tuples(self):
        planted = {'arthur': 'chapman', 'galahad': 'palin', 'robin': 'idle'}
        sut = Structure(**planted)
        items = sut.items()
        assert hasattr(items, '__iter__'), \
            'items() returned a %s.  Expected a sequence type' % type(items)
        expect(set(items)).to(equal(set(planted.items())))

    def test_cast_to_dict(self):
        expect(dict(Structure(**ARBITRARY_DICT))).to(equal(ARBITRARY_DICT))

    def test_to_dict_equality(self):
        expect(Structure(**ARBITRARY_DICT).to_dict()).to(equal(ARBITRARY_DICT))

    def test_to_dict_converts_nested_structures_to_dicts(self):
        dct = Structure(inner=Structure(biggles=2)).to_dict()
        expect(list(dct.values())[0]).to(be_a(dict))

    def test_to_dict_converts_nested_list_of_structures_to_list_of_dicts(self):
        key = 'biggles'
        value = 2
        dct = Structure(things=[Structure(**{key: value})]).to_dict()
        lst = list(dct.values())[0]
        expect(lst).to(be_a(list))
        inner = lst[0]
        expect(inner).to(be_a(dict))
        expect(inner[key]).to(equal(value))

    def test_to_and_from_json_dict(self):
        serialized = json.dumps(ARBITRARY_DICT)
        expect(json.loads(Structure.from_json(serialized).to_json())).to(
            equal(ARBITRARY_DICT))

    def test_can_add_item(self):
        key = 'i'
        value = 1
        sut = Structure()
        sut[key] = value
        expect(sut.to_dict()).to(contain_key_with_value(key, value))

    def test_can_add_attribute(self):
        key = 'i'
        value = 1
        sut = Structure()
        setattr(sut, key, value)
        expect(sut.to_dict()).to(contain_key_with_value(key, value))

    def test_len(self):
        expected = 42
        sut = Structure(**{'thing%d' % n: n for n in range(expected)})
        expect(len(sut)).to(equal(expected))

    def test_converts_list_of_dictionaries_to_list_of_structures(self):
        sut = Structure(things=[{'spam': 1}])
        expect(sut.things).to(be_a(list))
        expect(sut.things[0]).to(be_a(Structure))
        expect(sut.things[0].spam).to(equal(1))

    def test_holds_hash_constant(self):
        sut = Structure()
        baseline = hash(sut)
        sut['spams'] = 12
        expect(hash(sut)).to(equal(baseline))

    def test_has_unique_hash(self):
        expect(hash(Structure())).not_to(equal(hash(Structure())))

    def test_structures_with_same_keys_and_values_are_equal(self):
        members = {'larry': 'spam', 'moe': 42}
        expect(Structure(**members)).to(equal(Structure(**members)))

    def test_structures_with_same_nest_are_equal(self):
        members = {'manny': Structure(moe=1, jack=None)}
        expect(Structure(**members)).to(equal(Structure(**members)))

    def test_structure_with_different_keys_are_not_equal(self):
        s1 = Structure(spam=1, gravy=3)
        s2 = Structure(spam=1, pork=3)
        expect(s1).not_to(equal(s2))

    def test_structure_with_different_values_are_not_equal(self):
        s1 = Structure(spam=1, pork=True)
        s2 = Structure(spam=1, pork=3)
        expect(s1).not_to(equal(s2))

    def test_structure_is_not_equal_to_object_without_keys(self):
        expect(Structure()).not_to(equal([]))


if '__main__' == __name__:
    main()
