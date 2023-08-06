from .base import BasePattern
from .pattern_list import PatternTypes


class DigitalObjectIdentifier(BasePattern):
    """Finds DOIs (Digital Object Indetifiers) in a document

    A DOI is a persistent identifier composed of a prefix/suffix,
    like 10.1000/dome.12082.
    """

    TYPE = PatternTypes.DIGITAL_OBJECT_IDENTIFIER
    REGEX_FORMAT_STRING = r"(10\.\d{4,5}\/[\S]+[^;,.\s])"
