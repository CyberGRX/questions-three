from unittest import TestCase, main

from expects import expect, equal

from questions_three.vanilla import url_append


class TestUrlAppend(TestCase):
    def test_joins_arbitrary_number_of_strings(self):
        expect(url_append("spam/", "eggs/", "sausage/", "spam")).to(equal("spam/eggs/sausage/spam"))

    def test_introduces_one_slash_where_none_is_present(self):
        expect(url_append("spam", "eggs")).to(equal("spam/eggs"))

    def test_does_not_introduce_slash_when_trailing_is_present(self):
        expect(url_append("spam/", "eggs")).to(equal("spam/eggs"))

    def test_does_not_introduce_slash_when_leading_is_present(self):
        expect(url_append("spam", "/eggs")).to(equal("spam/eggs"))

    def test_eliminates_extra_slash_when_join_would_create_two(self):
        expect(url_append("spam/", "/eggs")).to(equal("spam/eggs"))

    def test_does_not_alter_two_trailing_slashes_from_same_string(self):
        expect(url_append("spam://", "eggs")).to(equal("spam://eggs"))

    def test_removes_leading_slash_from_part_following_two_slashes(self):
        expect(url_append("spam://", "/eggs")).to(equal("spam://eggs"))

    def test_ignores_none(self):
        expect(url_append("spam", None, "eggs")).to(equal("spam/eggs"))


if "__main__" == __name__:
    main()
