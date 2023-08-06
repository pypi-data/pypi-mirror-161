from .base import BasePattern
from .pattern_list import PatternTypes


class Ascii(BasePattern):
    """Looks for any ASCII character in a text"""

    REGEX_FORMAT_STRING = r"[ -~]"
    TYPE = PatternTypes.ASCII
