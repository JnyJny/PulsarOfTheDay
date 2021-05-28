"""
"""

from typing import List, Union

from astropy import units as u
from astropy.coordinates import Angle


def str_to_angle(
    value: str,
    metric: u.Unit = u.deg,
) -> Angle:
    """Given a J2000 dd:mm:ss string, convert to astropy.coordinates.Angle.

    If the string is missing fields, zeros are supplied from
    left to right.

    e.g.
    "+XX:YY" is converted to [XX, YY, 0.0]
    "+XX" is convrted to [XX, 0.0, 0.0]

    :param value: str
    :param metric: optional units.Unit, defaults to units.deg
    :return: astropy.coordinates.Angle
    """

    values = [float(f) for f in value.split(":")]

    # XXX Is this substitution right? I don't know :)
    # EJO this is junk
    missing = 3 - len(values)
    if missing:
        values.extend([0.0] * missing)

    return Angle(tuple(values), u.deg)


class Telescope:
    @classmethod
    def telescopes(cls) -> List["Telescope"]:
        return [
            cls("Arecibo", "-1:00:00", "37:30:00"),
            cls("CHIME", "-15:00:00", "90:00:00"),
            cls("FAST", "-14:12:00", "65:48:00"),
            cls("GBT", "-46:00:00", "90:00:00"),
            cls("VLA", "-44:00:00", "90:00:00"),
        ]

    @classmethod
    def observable_from(cls, declination: Union[Angle, str]) -> List[str]:
        """"""
        return [t.name for t in cls.telescopes() if t.can_see(declination)]

    def __init__(self, name: str, dec_lower: str, dec_upper: str) -> None:
        self.name = name
        self.lower = str_to_angle(dec_lower)
        self.upper = str_to_angle(dec_upper)

    def can_see(self, declination: Union[Angle, str]) -> bool:
        """True if this instrument can observe the given declination."""

        if isinstance(declination, str):
            declination = str_to_angle(declination)

        return declination.is_within_bounds(self.lower, self.upper)
