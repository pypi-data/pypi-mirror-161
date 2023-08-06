from .base import BasePattern
from .pattern_list import PatternTypes


class IpAddress(BasePattern):
    TYPE = PatternTypes.IP_ADDRESS
    REGEX_FORMAT_STRING = (
        r"(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)"
        r"(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}"
    )
    REGEX_FORMAT_STRING_IPV6 = (
        r"(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]"
        r"{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:"
        r"[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}"
        r"|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]"
        r"{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}"
        r"(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4})"
        r"{1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4})"
        r"{0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|"
        r"(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1"
        r"{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|"
        r"(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|"
        r"1{0,1}[0-9]){0,1}[0-9]))"
    )

    def __init__(self, is_v6: bool = False):
        self.is_v6 = is_v6
        super().__init__()

    def _compile(self) -> str:
        return self.REGEX_FORMAT_STRING_IPV6 if self.is_v6 else self.REGEX_FORMAT_STRING
