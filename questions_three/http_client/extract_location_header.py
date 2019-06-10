from questions_three.exceptions import InvalidHttpResponse


def extract_location_header(response):
    try:
        location = response.headers['Location']
    except KeyError as e:
        raise InvalidHttpResponse(
            f'HTTP {response.status_code} response '
            'lacks a location header') from e
    if '' == location:
        raise InvalidHttpResponse(
            f'HTTP {response.status_code} response '
            'contains an empty location header')
    return location
