from .base import BasePattern
from .pattern_list import PatternTypes


class SocialSecurityNumber(BasePattern):

    TYPE = PatternTypes.SSN
    REGEX_FORMAT_STRING = r"(?!0{3})(?!6{3})[0-8]\d{2}-(?!0{2})\d{2}-(?!0{4})\d{4}"
