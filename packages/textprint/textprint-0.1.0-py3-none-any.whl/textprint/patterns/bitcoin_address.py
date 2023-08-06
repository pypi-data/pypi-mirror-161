from .base import BasePattern
from .pattern_list import PatternTypes


class BitcoinAddress(BasePattern):
    """Looks for any bitcoin address in the text data.

    A bitcoin address must be unique. It's comprised of 25 to 39
    alphanumeric characters and the address usually begins with
    number 1 or 3, or bc1 for bech32 types.

    * P2PKH (Pay-to-Pub key hash) begins with number 1
    * P2SH (Pay-to-Scrypt Hash) begins with number 3
    * Bech32 addresses are a SegWit format starting with bc1
    """

    REGEX_FORMAT_STRING = r"\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b"
    TYPE = PatternTypes.BITCOIN_ADDRESS
