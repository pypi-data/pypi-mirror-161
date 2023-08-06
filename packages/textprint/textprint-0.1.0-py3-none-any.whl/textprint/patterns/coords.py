from collections import namedtuple
from typing import List

from .base import BasePattern
from .pattern_list import PatternTypes

Point = namedtuple("Point", ["lat", "lon"])


class GeographicCoordinates(BasePattern):
    """Detects geographic coordinates separated by a comma within text data

    Pattern has been fitted for Earth-like coordinates"""

    TYPE = PatternTypes.GEOGRAPHIC_COORDINATES
    REGEX_FORMAT_STRING = (
        r"(\+?\b(0?[0-9]|0?[1-9][0-9]|1[0-7][0-9]|180)\b(\.\d+)?|\-"
        r"?\b(0?[0-9]|0?[1-8][0-9]|90)\b(\.\d+)?),\s*(\+?\b(0?[0-9]"
        r"|0?[1-9][0-9]|[12][0-9][0-9]|3[0-5][0-9]|360)\b(\.\d+)?|"
        r"\-?\b(0?[0-9]|0?[1-9][0-9]|1[0-7][0-9]|180)\b(\.\d+)?)"
    )

    def to_coords(self, target_string: str) -> List[Point]:
        """Returns the parsed coordinates as an object with the latitude
        and longitude as floats

        :param target_string: the string to parse
        :type target_string: str
        :return: A list of coordinate objects Point(lat, lon)
        :rtype: List[Point]
        """
        matches = self.search(target_string)
        points = []

        for match in matches:
            lat, lon = match.split(",")
            points.append(Point(float(lat.strip(" +")), float(lon.strip(" +"))))

        return points
