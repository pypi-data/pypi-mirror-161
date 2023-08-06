import re

from .base import BasePattern
from .pattern_list import PatternTypes


class HyphenWordBreak(BasePattern):
    TYPE = PatternTypes.HYPHEN_WORD_BREAK
    REGEX_FORMAT_STRING = r"[a-zA-Z][\-]$[\n][a-zA-Z]"
    REGEX_SUBSTITUTION_PAIR = (r"([a-zA-Z])[\-]$[\n]([a-zA-Z])", "\\1\\2")

    def reassemble_text(self, target_string: str) -> str:
        regex, subst = self.REGEX_SUBSTITUTION_PAIR
        return re.sub(regex, subst, target_string, 0, re.MULTILINE)
