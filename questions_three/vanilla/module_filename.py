import os


def module_filename(module, filename):
    """
    Return the full path to a specific file inside a module
    """
    path, _ = os.path.split(module.__file__)
    return os.path.join(path, filename)
