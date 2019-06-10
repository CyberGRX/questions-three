from questions_three.exceptions import InvalidConfiguration


def numeric_value(*, key, val):
    try:
        return float(val)
    except ValueError as e:
        raise InvalidConfiguration(
            '"%s" was configured with a numeric value.  '
            'Refusing to override it with non-number "%s"'
            % (key, val)) from e


def bool_value(*, key, val):
    lc_val = str(val).lower()
    if lc_val in ('true', 'y', 'yes', '1'):
        return True
    if lc_val in ('false', 'n', 'no', '0'):
        return False
    raise InvalidConfiguration(
        '"%s" was configured with a boolean value.  '
        'Refusing to override it with "%s"'
        % (key, val))


def transform_type(*, key, val, new_type):
    if new_type == bool:
        return bool_value(key=key, val=val)
    if new_type in (int, float):
        return numeric_value(key=key, val=val)
    return val
