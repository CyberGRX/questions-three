def join(one, two):
    if not one:
        return two
    if one.endswith('/') and two.startswith('/'):
        return one + two[1:]
    if one.endswith('/') or two.startswith('/'):
        return one + two
    return '%s/%s' % (one, two)


def url_append(*parts):
    """
    Replacement for urljoin which
     1. Does not eliminate characters when slashes are present
     2. Joins an arbitrary number of parts
    """
    whole = ''
    for part in [p for p in parts if p]:
        whole = join(whole, part)
    return whole
