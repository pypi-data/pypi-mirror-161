import re

from .base import BasePattern
from .pattern_list import PatternTypes


class Username(BasePattern):
    """Pattern checking against any type of username with a defined length

    :param min_len: The minimal length of the username
    :type min_len: int
    :param max_len: The maximal length of the username
    :type max_len: int
    """

    TYPE = PatternTypes.USERNAME
    REGEX_FORMAT_STRING = r"\b[a-z0-9_-]{min_len,max_len}\b"

    def __init__(self, min_len: int, max_len: int):
        self.min_len = min_len
        self.max_len = max_len
        super().__init__()

    def _compile(self) -> str:
        return self.REGEX_FORMAT_STRING.replace("min_len", str(self.min_len)).replace(
            "max_len", str(self.max_len)
        )


class DiscordUsername(BasePattern):
    """Variant of the Username pattern checking against any Discord username in
    text data"""

    TYPE = PatternTypes.USERNAME
    REGEX_FORMAT_STRING = r"\b.{3,32}#[0-9]{4}\b"

    def __init__(self):
        super().__init__(flags=[re.M, re.I])
