from datetime import date
from typing import List

from .base import BasePattern
from .pattern_list import PatternTypes


class Date(BasePattern):
    """This expression will look for a date under the following formats in the text:
    * dd/mm/yyyy
    * dd-mm-yyyy
    * dd.mm.yyyy
    """

    TYPE = PatternTypes.DATE
    REGEX_FORMAT_STRING = (
        r"(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)"
        r"(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)"
        r"0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|"
        r"[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])"
        r"|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})"
    )

    def to_date(self, target_string: str) -> List[date]:
        """Converts the parsed dates in a date object

        :param target_string: The string to aprse dates on
        :type target_string: str
        :return: A list of date objects
        :rtype: List[date]
        """

        matches = self.search(target_string)
        dates = []

        for match in matches:
            for sep in "/-.":
                if len(match.split(sep)) == 3:
                    day, month, year = [int(el) for el in match.split(sep)]
                    break

            dates.append(date(year, month, day))

        return dates
