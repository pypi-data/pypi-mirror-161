import re

from .base import BasePattern
from .pattern_list import PatternTypes


class PanFromGstin(BasePattern):
    TYPE = PatternTypes.PAN_FROM_GSTIN
    REGEX_FORMAT_STRING = (
        r"([0][1-9]|[1-2][0-9]|[3][0-5])([a-zA-Z]{5}[0-9]{4}[a-zA-Z]"
        r"{1})([1-9a-zA-Z]{1}[zZ]{1}[0-9a-zA-Z]{1})+"
    )

    def __init__(self):
        super().__init__([re.M, re.I])
