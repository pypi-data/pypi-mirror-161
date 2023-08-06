from .base import BasePattern
from .pattern_list import PatternTypes


class Email(BasePattern):
    """
    Looks for any type of email in the text data.

    Note: the pattern used here is quite complex. You can look up here
    at https://ihateregex.io/expr/email-2/
    """

    REGEX_FORMAT_STRING = (
        r"""(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+")"""
        r""")@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]"""
        r"""+\.)+[a-zA-Z]{2,}))"""
    )
    TYPE = PatternTypes.EMAIL
