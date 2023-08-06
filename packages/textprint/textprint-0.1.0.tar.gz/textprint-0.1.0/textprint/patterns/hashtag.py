import re

from .base import BasePattern
from .pattern_list import PatternTypes


class Hashtag(BasePattern):
    TYPE = PatternTypes.HASHTAG
    REGEX_FORMAT_STRING = r"#\b[^\s!@#$%^&*(),.?\":{}|<>]*\b"

    def __init__(self):
        super().__init__([re.M, re.I])
