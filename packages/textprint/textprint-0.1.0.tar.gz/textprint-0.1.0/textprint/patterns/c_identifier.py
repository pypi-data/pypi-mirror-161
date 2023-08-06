from .base import BasePattern
from .pattern_list import PatternTypes


class CLanguageIdentifier(BasePattern):
    """Looks for identifiers deriving from C within text data.

    Identifiers are also called tokens or symbols, naming language entities, like
    variables, structures, functions, etc...

    It can also be used for languages deriving from C, like C++, Python, Java,
    JavaScript, etc...
    """

    TYPE = PatternTypes.C_IDENTIFIER
    REGEX_FORMAT_STRING = r"\b[a-zA-Z_][0-9a-zA-Z_]*$\b"
