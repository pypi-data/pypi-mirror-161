from .base import BasePattern
from .pattern_list import PatternTypes


class Emoji(BasePattern):
    """
    Identifies emojis in the text.

    Emojis can be translated as unicode characters as denoted in the
    unicode standard: https://www.unicode.org/Public/emoji/12.1/emoji-data.txt

    Warning: the emoji pattern wasn't tested properly as some of them had an unexpected
    result
    """

    TYPE = PatternTypes.EMOJI
    REGEX_FORMAT_STRING = (
        r"(\u00a9|\u00ae|[\u2000-\u3300]|\ud83c[\ud000-\udfff]|"
        r"\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff])"
    )
    # TODO : import directly from emoji-sequences and emoji-zwj-sequences
    # TODO : fetch data here https://unicode.org/Public/emoji/version/*.txt
