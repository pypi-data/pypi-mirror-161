from .base import BasePattern
from .pattern_list import PatternTypes


class CreditCardNumber(BasePattern):
    """Detects a credit card number in the text data

    Currenctly works for the following types:

    1 - Visa
    2 - MasterCard
    3 - American Express
    4 - Diners Club
    5 - Discover
    6 - JCB
    """

    TYPE = PatternTypes.CREDIT_CARD_NUMBER
    REGEX_FORMAT_STRING = (
        r"(^4[0-9]{12}(?:[0-9]{3})?$)|(^(?:5[1-5][0-9]{2}|222[1-9]"
        r"|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$)|(3[47][0-9]{13})|"
        r"(^3(?:0[0-5]|[68][0-9])[0-9]{11}$)|(^6(?:011|5[0-9]{2})[0-9]{12}$)|"
        r"(^(?:2131|1800|35\d{3})\d{11}$)"
    )
