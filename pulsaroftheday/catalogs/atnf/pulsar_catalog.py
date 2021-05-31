"""a Pandas DataFrame loader for ATNF Pulsar Catalogue v1.64 data.
"""

import importlib.resources as ir

from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple, Union

import numpy as np
import pandas as pd
import wikipediaapi as wiki

from astropy import units as u
from astropy.coordinates import SkyCoord
from loguru import logger

from ..telescope import Telescope
from .plots import generate_pdot_skymap_plots


def fix_angle(text: str, dms: bool = True) -> str:

    fields = text.split(":")
    angle_spec = "{}d{}m{}s" if dms else "{}h{}m{}s"

    try:
        return angle_spec.format(*fields)
    except IndexError:
        pass
    try:
        return angle_spec[:-3].format(*fields)
    except IndexError:
        pass
    return angle_spec[:-6].format(*fields)


def galactic_coords(ra: str, dec: str) -> Tuple[float, float]:
    """Galactic latitude & longitude in radians from RA and DEC."""

    gc = SkyCoord(
        ra=fix_angle(ra, dms=False),
        dec=fix_angle(dec),
        unit=(u.hourangle, u.deg),
        frame="icrs",
    ).galactic

    g_lat = gc.l.wrap_at(180 * u.deg).radian
    g_long = gc.b.radian

    return (g_lat, g_long)


class PulsarCatalog:
    """A pandas DataFrame loader for ATNF Pulsar Catalogue v1.64 data.

    Source Data:
    https://www.atnf.csiro.au/research/pulsar/psrcat/
    Manchester, R. N., Hobbs, G. B., Teoh, A. & Hobbs, M., Astron. J.,
    129, 1993-2006 (2005) (astro-ph/0412641)

    """

    def __init__(self, csv_path: Union[str, Path]) -> None:
        """Initialize a catalog with the path to a CSV file.

        If the CSV file does not exist, PulsarCatalog will
        create a new DataFrame populated with the ATNF Pulsar
        catalogue v1.64 data that is included with the tool.

        If the CSV file does exist, the original catalog data
        is ignored and data is loaded from the CSV file.

        The CSV file is not updated until the `PulsarCatalog.write`
        method is called explicitly.

        :param csv_path: Union[str, Path]
        """
        self.csv_path = Path(csv_path)

    @property
    def source_url(self) -> str:
        """Data source URL."""
        # XXX at some point it would be cool to pull the data
        #     from http instead of embedding a copy of the database
        #     in the shipping tool.
        return "https://www.atnf.csiro.au/research/pulsar/psrcat/"

    @property
    def catalog_keys(self) -> List[str]:
        return ["NAME", "PSRB", "PSRJ", "RAJ", "DECJ", "F0", "F1"]

    @property
    def tweetable_keys(self) -> List[str]:
        return [
            "NAME",
            "RAJ",
            "DECJ",
            "period",
            "pdot",
            "DM",
            "char_age",
            "b_s",
            "g_lat",
            "g_long",
        ]

    @property
    def dataframe(self) -> pd.DataFrame:
        """A pandas.DataFrame loaded with pulsar data."""

        try:
            return self._dataframe
        except AttributeError:
            pass

        try:
            self._dataframe = pd.read_csv(self.csv_path)
        except Exception as error:
            logger.debug(f"{error}")
            pulsars = self.load_psrcat()
            self._dataframe = pd.DataFrame(data=list(pulsars.values()))
            logger.debug(f"Read {len(self._dataframe)} items.")

        self._dataframe["NAME"] = self._dataframe.PSRB.combine_first(
            self._dataframe.PSRJ
        )

        self._dataframe["CNAME"] = self._dataframe.PSRB.str.cat(
            self._dataframe.PSRJ, sep=" ", na_rep="?"
        )

        self._dataframe["freq"] = self._dataframe.F0
        self._dataframe["fdot"] = self._dataframe.F1
        self._dataframe["period"] = 1 / self._dataframe.freq
        self._dataframe["pdot"] = (
            -1 / (self._dataframe.freq ** 2)
        ) * self._dataframe.fdot

        self._dataframe["char_age"] = self._dataframe.period / (
            2 * self._dataframe.pdot
        )

        # np.seterr(all="raise")
        try:
            self._dataframe["b_s"] = (
                1e12
                * np.sqrt(self._dataframe.pdot / 1e-15)
                * np.sqrt(self._dataframe.period / u.s)
                * u.G
            )
        except Exception as error:
            logger.debug(f"B_S {error}")

        # np.seterr(all="ignore")

        self._dataframe["color"] = "lightblue"
        self._dataframe["tweeted"] = np.NaN

        self._dataframe.index.rename("INDEX", inplace=True)

        return self._dataframe

    @property
    def tweetable(self) -> pd.DataFrame:
        """A pandas.DataFrame containing a subset of Pulsars with valid data.

        Valid entries (not NaN) for these keys:
        - NAME, period, pdot, g_lat, g_long


        The dataframe will retain all the columns.
        """
        return self.dataframe.dropna(
            subset=["NAME", "period", "pdot", "g_lat", "g_long"]
        )

    @property
    def default_catalog_path(self) -> Path:
        """Default path for ATFN Pulsar Catalogue v1.64 data."""

        try:
            return self._default_catalog_path
        except AttributeError:
            pass
        with ir.path("pulsaroftheday.catalogs.atnf.data", "psrcat.db") as db:
            self._default_catalog_path = db
        return self._default_catalog_path

    @property
    def wikipedia(self) -> wiki.Wikipedia:
        """"""
        try:
            return self._wikipedia
        except AttributeError:
            pass

        self._wikipedia = wiki.Wikipedia("en")

        return self._wikipedia

    def initialize(self, force: bool = False) -> None:

        if not force:
            logger.info("Initialize: no action taken when force=False")
            logger.info("Actions that would be taken:")
            logger.info(f"- unlink {self.csv_path}")
            logger.info(f"- delete the existing dataframe from memory.")
            logger.info(f"- re-read data from {self.default_catalog_path}")
        else:
            logger.info("Beginning catalog initialization")
            self.csv_path.unlink(missing_ok=True)
            logger.success(f"Unlinked {self.csv_path}")
            del self._dataframe
            logger.success("Removed existing dataframe")
            self.dataframe
            logger.success(f"Dataframe read from {self.default_catalog_path}")
            if self.dataframe.empty:
                logger.error("Re-initialized dataframe is empty!")
                raise Exception("Need a better empty catalog exception")
            logger.success(f"Reloaded {len(self.dataframe)} pulsars")
            self.save()
            logger.success(f"Wrote cached CSV database to {self.csv_path}")

    def load_psrcat(
        self, psrcat_path: Union[str, Path] = None
    ) -> Dict[str, Dict[str, str]]:
        """Create a dictionary of pulsar records keyed by name.

        If `psrcat_path` is unspecified, the default catalog is loaded.

        :param psrcat_path: Union[str, Path]
        """
        pulsars = {}

        psrcat_path = Path(psrcat_path or self.default_catalog_path)

        logger.debug(f" {psrcat_path} {psrcat_path.exists()}")

        with psrcat_path.open() as db:
            record = []
            names = []
            for line in db:
                if line.startswith("#"):
                    continue
                if line.startswith("@-"):
                    pulsar = pulsars.setdefault(names[0], {})
                    for attr, value in record:
                        pulsar.update({attr: value})
                    record = []
                    names = []
                    continue

                parameter, value, *items = line.split()

                if parameter not in ["DECJ", "RAJ"]:
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        pass

                record.append((parameter, value))
                if parameter in ["PSRJ", "PSRB"]:
                    names.append(value)
                    names.sort()  # B names moved to front

        for name, pulsar in pulsars.items():
            try:
                g_lat, g_long = galactic_coords(
                    pulsar["RAJ"],
                    pulsar["DECJ"],
                )
                pulsar.setdefault("g_lat", g_lat)
                pulsar.setdefault("g_long", g_long)
            except KeyError as error:
                logger.debug(f"{name} Missing key {error}")

        return pulsars

    def random_pulsar_population(
        self,
        pop_count: int = 0,
        include_name: str = None,
        required_keys: List[str] = None,
    ) -> pd.DataFrame:
        """Return a pandas.DataFrame with a random pulsar population.

        If `pop_count` is zero, returns the entire dataframe in random
        order.

        If `include_name` is given and found in the dataframe, the
        record for that pulsar is inserted at the top of the dataframe.

        If `required_keys` are given the catalog dataframe is narrowed
        to just those keys.

        :param pop_count: int
        :param include_name: optional str
        :param required_keys: optional List[str]
        :return: pandas.DataFrame
        """

        df = self.tweetable

        pop_count = pop_count or len(df)

        if required_keys:
            df = df[required_keys]

        sample = df.sample(pop_count)

        if include_name:
            match = df[df.CNAME.str.contains(include_name, regex=False)]
            logger.info(f"Matched {len(match)} records for {include_name}")
            if not match.empty:
                sample = match.append(sample).drop_duplicates()

        return sample

    def plot_random_population(
        self,
        path: Union[str, Path],
        pop_count: int = 0,
        include_name: str = None,
        target_color: str = "red",
        animated: bool = True,
    ) -> Tuple:

        sample = self.random_pulsar_population(pop_count, include_name)

        sample.loc[sample.head(1).index[0], "color"] = "red"

        generate_pdot_skymap_plots(sample, path)

        return [t for t in sample.head(1).itertuples(name="Pulsar")][0]

    def tweet_text(self, pulsar_name: str) -> str:
        """"""
        df = self.tweetable

        logger.debug(f"{pulsar_name} in  {len(df)} records?")

        match = df[df.CNAME.str.contains(pulsar_name, regex=False)]

        logger.info(f"Matched {len(match)} records for {pulsar_name}")

        if match.empty or len(match) > 1:
            raise Exception(f"No match for {pulsar_name}")

        df = match[self.tweetable_keys]

        for p in df.itertuples():

            lines = [
                f"Pulsar: {p.NAME}",
                f"RA: {p.RAJ}",
                f"Dec: {p.DECJ}",
                f"Period: {round(p.period, 3)} s",
                f"Pdot: {p.pdot:.3e}",
                f"DM: {p.DM} pc/cm^3",
                f"Characteristic Age: {p.char_age:.3e} yr",
                f"Surface Magnetic Field: {p.b_s:.3e} G",
            ]

            for key in ["PSRJ", "PSRB"]:
                try:
                    name = getattr(p, key)
                    page = self.wikipedia.page(f"PSR_{name}")
                except (KeyError, AttributeError):
                    continue
                if page.exists():
                    lines.append(f"Wikipedia URL: {page.canonicalurl}")
                    break

            visible_to = Telescope.observable_from(p.DECJ)
            if visible_to:
                lines.append(f"Visible from {', '.join(visible_to)}")

            return "\n".join(lines)

    def tweet(self, df: pd.DataFrame) -> Generator[str, None, None]:

        for p in df[self.tweetable_keys].itertuples():

            lines = [
                f"Pulsar: {p.NAME}",
                f"RA: {p.RAJ}",
                f"Dec: {p.DECJ}",
                f"Period: {round(p.period, 3)} s",
                f"Pdot: {p.pdot:.3e}",
                f"DM: {p.DM} pc/cm^3",
                f"Characteristic Age: {p.char_age:.3e} yr",
                f"Surface Magnetic Field: {p.b_s:.3e} G",
            ]

            for key in ["PSRJ", "PSRB"]:
                try:
                    name = getattr(p, key)
                    page = self.wikipedia.page(f"PSR_{name}")
                except (KeyError, AttributeError):
                    continue
                if page.exists():
                    lines.append(f"Wikipedia URL: {page.canonicalurl}")
                    break

            visible_to = Telescope.observable_from(p.DECJ)
            if visible_to:
                lines.append(f"Visible from {', '.join(visible_to)}")

            yield "\n".join(lines)

    def save(self):
        """"""
        self.write_csv(self.csv_path)

    def write_csv(
        self,
        path: Union[str, Path] = None,
        keys: List[str] = None,
        dropna: bool = False,
    ) -> None:
        """Write the contents of `dataframe` to `path` in CSV format.

        :param path: Union[str, Path]
        :param keys: optional List[str]
        :param dropna: optional bool
        """

        df = self.dataframe[keys] if keys else self.dataframe

        if dropna:
            df = df.dropna()

        text = df.to_csv(path, index=False, index_label=None)

        if not path:
            print(text)
