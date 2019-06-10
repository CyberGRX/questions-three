import questions_three.exceptions.http_error as error


def extract_error_classes():
    return [
        getattr(error, name)
        for name in dir(error)
        if not name.startswith('_')]


ERROR_CLASSES = [
    cls for cls in extract_error_classes()
    if issubclass(cls, error.HttpError)]


STATUS_GROUP_HEADS = {
    cls.status_group: cls
    for cls in ERROR_CLASSES
    if cls.status_group is not None and cls.status_code is None}


BY_STATUS_CODE = {
    cls.status_code: cls
    for cls in ERROR_CLASSES
    if cls.status_code}


def class_matching_status_code(code):
    if code in BY_STATUS_CODE.keys():
        return BY_STATUS_CODE[code]
    return None


def group_head_matching_status_code(code):
    group = int(code / 100)
    if group in STATUS_GROUP_HEADS.keys():
        return STATUS_GROUP_HEADS[group]
    return None


def inspect_response(resp):
    code = int(resp.status_code)
    cls = (
        class_matching_status_code(code) or
        group_head_matching_status_code(code))
    if cls:
        raise cls(resp.text, response=resp)
