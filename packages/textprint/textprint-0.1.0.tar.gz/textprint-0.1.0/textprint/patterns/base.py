import re
from typing import List

from .pattern_list import PatternTypes


class BasePattern:
    """BasePattern for all pattern classes.

    Compiles into a regex pattern firsthand before processing any passed string.

    :param flags: The necessary `re` flags for the pattern compilation, defaults
    to [re.M]
    :type flags: List[re.RegexFlag], optional
    """

    REGEX_FORMAT_STRING = r""
    TYPE = PatternTypes.BASE

    @staticmethod
    def sum_regex_flags(flags: List[re.RegexFlag]) -> int:
        """Method summing regex flags for the compilation

        :param flags: list of regex flags like MULTILINE or IGNORECASE
        :type flags: List[re.RegexFlag]
        :return: An union of flags
        :rtype: int
        """
        flag_id = flags[0]
        for flag in flags[1:]:
            flag_id = flag_id | flag
        return flag_id

    def __init__(self, flags: List[re.RegexFlag] = [re.M]):
        self.flags = self.sum_regex_flags(flags)

    def _compile(self) -> str:
        """Abstract method for compile

        :return: The string to compile
        :rtype: str
        """
        return self.REGEX_FORMAT_STRING

    def compile(self) -> None:
        self.regex_pattern = re.compile(self._compile(), flags=self.flags)

    def search(self, target_string: str) -> List[str]:
        """Given some text, will look for several instances of the pattern and return a
        list of matches. Only takes the base group as the main result.

        :param target_string: The string to perform a search on.
        :type target_string: str
        :return: A list of matches or an empty list if no pattern was found
        :rtype: List[str]
        """
        if not hasattr(self, "regex_pattern"):
            self.compile()

        regex_matches = self.regex_pattern.finditer(target_string)
        return [m.group() for m in regex_matches]

    def __str__(self):
        return f"Parser for {self.TYPE}"
