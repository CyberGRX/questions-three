class FormElementLacksAction(RuntimeError):
    """
    The form element lacks an "action" attribute
    """


class FormElementLacksMethod(RuntimeError):
    """
    The form element lacks a "method" attribute
    """


class FormNotFound(RuntimeError):
    """
    The specified HTML form was not found on the page
    """
