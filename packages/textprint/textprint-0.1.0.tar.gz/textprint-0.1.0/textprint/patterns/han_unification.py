from .base import BasePattern
from .pattern_list import PatternTypes


class HanUnification(BasePattern):
    """Detects Chinese-like characters for the 3 most popular Far East languages

    * Japanese (kanji-only)
    * Korean (hanja-only)
    * Chinese (hanzi)
    """

    TYPE = PatternTypes.HAN_UNIFICATION
    REGEX_FORMAT_STRING = (
        r"^[\u4E00-\u9FFF\u3400-\u4DBF\u20000-\u2A6DF\u2A700-"
        r"\u2B73F\u2B740-\u2B81F\u2B820-\u2CEAF\u2CEB0-\u2EBEF\u30000-\u3134F"
        r"\uF900-\uFAFF\u2E80-\u2EFF\u31C0-\u31EF\u3000-\u303F\u2FF0-\u2FFF\u3300-"
        r"\u33FF\uFE30-\uFE4F\uF900-"
        r"\uFAFF\u2F800-\u2FA1F\u3200-\u32FF\u1F200-\u1F2FF\u2F00-\u2FDF]+$"
    )
