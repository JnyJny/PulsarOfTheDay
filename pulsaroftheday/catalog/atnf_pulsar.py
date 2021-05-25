""" ATNF Catalogue Pulsar Record
"""

import importlib.resources as ir

from dataclasses import dataclass
from pathlib import Path

from typing import Any, Dict, List, Union

import numpy as np
import wikipediaapi as wiki

from astropy import units as u
from astropy.units import Quantity
from astropy.coordinates import Angle
from astropy.coordinates import SkyCoord
from loguru import logger


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

    def __init__(self, name: str, dec_lower: str, dec_upper: str) -> None:
        self.name = name
        self.lower = str_to_angle(dec_lower)
        self.upper = str_to_angle(dec_upper)

    def can_see(self, declination: Angle) -> bool:
        """True if this instrument can observe the given declination."""
        return declination.is_within_bounds(self.lower, self.upper)


@dataclass
class ATNFPulsar:
    NAME: str
    PSRB: str
    PSRJ: str
    RAJ: str
    DECJ: str
    F0: float
    F1: float
    DM: float

    # properties with:
    # - uppercase names are the values straight from the catalog
    # - lowercase names are derived from the uppercase names

    @classmethod
    def keys(cls) -> List[str]:
        return list(cls.__dataclass_fields__.keys())

    def __str__(self) -> str:
        """"""
        lines = []
        lines.append(f"Pulsar: {self.NAME}")
        lines.append(f"RA: {self.RAJ}")
        lines.append(f"Dec: {self.DECJ}")
        lines.append(f"Period: {self.period}")
        lines.append(f"Pdot: {self.pdot}")
        lines.append(f"DM: {self.dm}")
        lines.append(f"Characteristic Age: {self.char_age}")
        lines.append(f"Surface magnetic field: {self.b_s}")

        if self.visible_telescopes:
            lines.append(f"Visible from {', '.join(self.visible_telescopes)}")
        if self.wikipedia_url:
            lines.append(f"Wikipedia: {self.wikipedia_url}")

        return "\n".join(lines)

    @property
    def wikipedia_url(self) -> Union[str, None]:
        """Wikipedia URL for this Pulsar (if it exists)."""
        try:
            return self._wikipedia_url
        except AttributeError:
            pass

        try:
            wikipedia = wiki.Wikipedia("en")

        except Exception as error:
            logger.debug(f"{error} contacting wikipedia. <retry>")
            return None

        for name in [self.PSRB, self.PSRJ]:
            page = wikipedia.page(f"PSR_{name}")
            if page.exists():
                self._wikipedia_url = page.canonicalurl
                logger.info(f"{self.NAME}:{name} -> {page.canonicalurl}")
                break
        else:
            self._wikipedia_url = None
            logger.debug(f"No wikipedia page for {self.NAME}")

        return self._wikipedia_url

    @property
    def ra(self) -> Angle:
        """Right ascension (J2000) (hh:mm:ss.s)"""
        try:
            return self._ra
        except AttributeError:
            pass
        self._ra = str_to_angle(self.RAJ)
        return self._ra

    @property
    def dec(self) -> Angle:
        """Declination (J2000) (+dd:mm:ss)"""
        try:
            return self._dec
        except AttributeError:
            pass
        self._dec = str_to_angle(self.DECJ)
        return self._dec

    @property
    def freq(self) -> float:
        """Barycentric rotation frequency (Hz)."""
        return self.F0

    @property
    def fdot(self) -> float:
        """Time derivative of barycentric period (dimensionless)."""
        return self.F1

    @property
    def period(self) -> Quantity:
        """Rotational period, inverse of self.freq."""
        try:
            return self._period
        except AttributeError:
            pass
        self._period = (1 / self.freq) * u.s
        return self._period

    @property
    def pdot(self) -> float:
        """???"""
        try:
            return self._pdot
        except AttributeError:
            pass
        self._pdot = -1 * (1 / self.freq ** 2) * self.fdot
        return self._pdot

    @property
    def dm(self) -> Quantity:
        """Dispersion measure (cm^3 pc)."""
        try:
            return self._dm
        except AttributeError:
            pass
        self._dm = self.DM * (u.pc / u.cm ** 3)
        return self._dm

    @property
    def char_age(self) -> Quantity:
        """Characteristic age in X years."""
        try:
            return self._char_age
        except AttributeError:
            pass
        self._char_age = (self.period / (2 * self.pdot)).to(u.yr)
        return self._char_age

    @property
    def b_s(self) -> Quantity:
        """Surface magnetic field in Guass."""
        try:
            return self._b_s
        except AttributeError:
            pass

        BigMagicNumber = 1e12
        LittleMagicNumber = 1e-15

        self._b_s = BigMagicNumber

        try:
            # If any of the arguments to np.sqrt is negative, will raise the
            # RuntimeWarning as an exception and log it as an error.
            # Not sure what it means when pdot is < 0.
            with np.errstate(invalid="raise"):
                self._b_s *= np.sqrt(self.pdot / LittleMagicNumber)
                self._b_s *= np.sqrt(self.period / u.s)

        except Exception as error:
            logger.error(f"{self.NAME} {error} pdot={self.pdot} period={self.period}")
            self._b_s = 0

        self._b_s *= u.G

        return self._b_s

    @property
    def visible_telescopes(self) -> List[str]:
        """List of telescopes where this pulsar is observable."""
        try:
            return self._visible_telescopes
        except AttributeError:
            pass

        self._visible_telescopes = [
            t.name for t in Telescope.telescopes() if t.can_see(self.dec)
        ]

        return self._visible_telescopes
