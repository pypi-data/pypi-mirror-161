from .base import BasePattern
from .pattern_list import PatternTypes


class SemanticVersioning(BasePattern):
    TYPE = PatternTypes.SEMANTIC_VERSIONING
    REGEX_FORMAT_STRING = (
        r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]"
        r"\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*"
        r"[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\."
        r"[0-9a-zA-Z-]+)*))?"
    )
