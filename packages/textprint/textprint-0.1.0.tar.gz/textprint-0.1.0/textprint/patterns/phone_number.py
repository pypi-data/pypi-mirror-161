import re
from typing import List, Optional

from .base import BasePattern
from .pattern_list import PatternTypes


class PhoneNumber(BasePattern):
    """Pattern checking against a phone number (regular or E164)"""

    REGEX_FORMAT_STRING = r"[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}"
    REGEX_FORMAT_STRING_E164 = r"\+[1-9]\d{1,14}"
    TYPE = PatternTypes.PHONE_NUMBER

    def __init__(
        self,
        is_e164: Optional[bool] = False,
        flags: List[re.RegexFlag] = [re.M, re.IGNORECASE],
    ) -> None:
        self.is_e164 = is_e164
        super().__init__(flags=flags)

    def _compile(self) -> str:
        return (
            self.REGEX_FORMAT_STRING_E164 if self.is_e164 else self.REGEX_FORMAT_STRING
        )
