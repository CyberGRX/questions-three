from expects import expect, equal
from functools import partial
from unittest import TestCase, main

from twin_sister.expects_matchers import raise_ex
from questions_three.vanilla import string_of_sequential_characters


class TestGenerateRandomString(TestCase):

    def test_generates_correct_string_length(self):
        expected_length = 84

        generated = string_of_sequential_characters(
            character_count=expected_length)

        expect(len(generated)).to(equal(expected_length))

    def test_same_string_returned_with_different_calls(self):
        generated1 = string_of_sequential_characters(
            character_count=100)
        generated2 = string_of_sequential_characters(
            character_count=100)

        expect(generated1).to(equal(generated2))

    def test_generates_string_with_100000_characters(self):
        expected_length = 100000

        generated = string_of_sequential_characters(
            character_count=expected_length)

        expect(len(generated)).to(equal(expected_length))

    def test_same_100000_character_string_returned_with_different_calls(self):
        generated1 = string_of_sequential_characters(
            character_count=100000)
        generated2 = string_of_sequential_characters(
            character_count=100000)

        expect(generated1).to(equal(generated2))

    def test_raises_exception_if_integer_not_given(self):
        test = partial(string_of_sequential_characters, character_count=True)

        expect(test).to(raise_ex(TypeError))

    def test_raises_exception_if_negative_integer_given(self):
        count = -10

        test = partial(string_of_sequential_characters, character_count=count)

        expect(test).to(raise_ex(TypeError))


if __name__ == '__main__':
    main()
