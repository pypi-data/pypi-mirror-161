from .base import BasePattern
from .pattern_list import PatternTypes


class UrlSlug(BasePattern):
    TYPE = PatternTypes.URL_SLUG
    REGEX_FORMAT_STRING = r"[a-z0-9]+(?:-[a-z0-9]+)*"
