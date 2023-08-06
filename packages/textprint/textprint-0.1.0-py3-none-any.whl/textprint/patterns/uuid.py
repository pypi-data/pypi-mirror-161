from .base import BasePattern
from .pattern_list import PatternTypes


class Uuid(BasePattern):
    TYPE = PatternTypes.UUID
    REGEX_FORMAT_STRING = (
        r"[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-"
        r"[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}"
    )
