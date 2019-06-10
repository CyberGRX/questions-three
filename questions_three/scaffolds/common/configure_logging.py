import logging

from twin_sister import dependency

from questions_three.logging.constants import \
    MESSAGE_FORMAT as LOG_MESSAGE_FORMAT


def configure_logging():
    dependency(logging).basicConfig(
        format=LOG_MESSAGE_FORMAT,
        level=logging.INFO)
