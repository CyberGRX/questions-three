from urllib.parse import urlparse

from questions_three.vanilla import url_append


def construct_redirect_url(*, request_url, response_location_header):
    parsed_request = urlparse(request_url)
    parsed_location = urlparse(response_location_header)
    if parsed_location.scheme:
        redirect = response_location_header
    else:
        redirect = url_append(
            f'{parsed_request.scheme}://{parsed_request.netloc}',
            response_location_header)
    parsed_redirect = urlparse(redirect)
    if parsed_request.fragment and not parsed_redirect.fragment:
        redirect += f'#{parsed_request.fragment}'
    return redirect
