from .base import BasePattern
from .pattern_list import PatternTypes


class Password(BasePattern):
    TYPE = PatternTypes.PASSWORD
    REGEX_FORMAT_STRING = (
        r"(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{min_len,}"
    )

    def __init__(self, min_len: int):
        super().__init__()
        self.min_len = min_len

    def _compile(self) -> str:
        return self.REGEX_FORMAT_STRING.replace("min_len", str(self.min_len))
