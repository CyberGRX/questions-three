from random import randint
from string import ascii_lowercase, digits


BASE36_CHARS = digits + ascii_lowercase


def random_base36_string(length):
    return ''.join([
        BASE36_CHARS[randint(0, len(BASE36_CHARS)-1)]
        for n in range(length)])
