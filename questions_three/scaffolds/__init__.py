from .common import activate_reporters


def disable_default_reporters():
    activate_reporters.enabled = False


def enable_default_reporters():
    activate_reporters.enabled = True
