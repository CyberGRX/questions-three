from base64 import b16encode
from unittest import TestCase, main

from expects import expect, equal

from questions_three.vanilla import b16encode_str


class TestB16encodeStr(TestCase):

    def test_encoding(self):
        subject = '%#$FREW. .@2!'
        expect(
            b16encode_str(subject)).to(
                equal(
                    b16encode(bytes(subject, 'utf-8')).decode(
                        'utf-8')))


if '__main__' == __name__:
    main()
