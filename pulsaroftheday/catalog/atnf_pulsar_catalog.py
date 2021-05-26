"""a Pandas DataFrame loader for ATNF Pulsar Catalogue v1.64 data.
"""

import importlib.resources as ir

from pathlib import Path
from typing import Any, Dict, Generator, List, Union

import pandas as pd

from loguru import logger

from .atnf_pulsar import ATNFPulsar as Pulsar


class ATNFPulsarCatalog:
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
    def dataframe(self) -> pd.DataFrame:
        """A pandas.DataFrame loaded with pulsar data."""

        try:
            return self._dataframe
        except AttributeError:
            pass

        try:
            self._dataframe = pd.read_csv(self.csv_path)
            if not self._dataframe.empty:
                return self._dataframe
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

        self._dataframe["color"] = "lightblue"

        self._dataframe.index.rename("INDEX", inplace=True)

        return self._dataframe

    @property
    def plottable(self) -> pd.DataFrame:
        """A pandas.DataFrame containing a subset of Pulsars with valid data.

        The dataframe will have values for:
        NAME, PSRB, PSRJ, RAJ, DECJ, F0, F1, and DM

        The dataframe will retain all the columns.
        """
        return self.dataframe[Pulsar.keys()].dropna(
            subset=["NAME", "RAJ", "DECJ", "F0", "F1"]
        )

    @property
    def default_catalog(self) -> Path:
        """Default path for ATFN Pulsar Catalogue v1.64 data."""

        try:
            return self._default_catalog
        except AttributeError:
            pass
        with ir.path("pulsaroftheday.catalog.data", "psrcat.db") as db:
            self._default_catalog = db
        return self._default_catalog

    def initialize(self, force: bool = False) -> None:

        if force:
            logger.info("Beginning catalog initialization")
            self.csv_path.unlink(missing_ok=True)
            logger.success(f"Unlinked {self.csv_path}")
            del self._dataframe
            logger.success("Removed existing dataframe")
            self.dataframe
            logger.success(f"Dataframe read from {self.default_catalog}")
            if self.dataframe.empty:
                logger.error("Re-initialized dataframe is empty!")
                raise Exception("Need a better empty catalog exception")
            logger.success(f"Reloaded {len(self.dataframe)} pulsars")
            self.save()
            logger.success(f"Wrote cached CSV database to {self.csv_path}")
            return

        logger.info("Initialize: no action taken when force=False")
        logger.info("Actions that would be taken:")
        logger.info(f"- unlink {self.csv_path}")
        logger.info(f"- delete the existing dataframe from memory.")
        logger.info(f"- re-read data from {self.default_catalog}")

    def load_psrcat(
        self, psrcat_path: Union[str, Path] = None
    ) -> Dict[str, Dict[str, str]]:
        """Create a dictionary of pulsar records keyed by name.

        If `psrcat_path` is unspecified, the default catalog is loaded.

        :param psrcat_path: Union[str, Path]
        """
        pulsars = {}

        psrcat_path = Path(psrcat_path or self.default_catalog)

        logger.debug(f"psrcat {psrcat_path}")

        with psrcat_path.open() as db:
            record = []
            names = []
            for line in db:
                if line.startswith("#"):
                    continue
                if line.startswith("@-"):
                    info = pulsars.setdefault(names[0], {})
                    for attr, value in record:
                        info.update({attr: value})
                    record = []
                    names = []
                    continue
                parameter, value, *items = line.split()

                try:
                    value = float(value)
                except (ValueError, TypeError):
                    pass

                record.append((parameter, value))
                if parameter in ["PSRJ", "PSRB"]:
                    names.append(value)
                    names.sort()  # B names moved to front

        # XXX
        # calculate period, pdot, glat, glong, char_age, and whatnot?

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

        If `required_keys` are given the catalog dataframe is plottableed
        to just those keys.

        :param pop_count: int
        :param include_name: optional str
        :param required_keys: optional List[str]
        :return: pandas.DataFrame
        """

        pop_count = pop_count or len(self.dataframe)

        df = self.dataframe

        if required_keys:
            df = df[required_keys]

        sample = df.sample(pop_count)

        if include_name:
            match = df.CNAME.str.contains(include_name, regex=False)
            logger.info(f"Matched {len(match)} records for {include_name}")
            if match:
                sample = match.append(sample).drop_duplicates()

        return sample

    def iter_all_pulsars(self) -> Generator[Pulsar, None, None]:
        """A generator that yields an ATNFPUlsar for all pulsars in the catalog."""
        for values in self.dataframe[Pulsar.keys()].itertuples(index=False):
            yield Pulsar(*values)

    def iter_plottable_pulsars(
        self,
    ) -> Generator[Pulsar, None, None]:
        """A generator that yields an ATNFPulsar for each plottable pulsar in the catalog."""
        for values in self.plottable.itertuples(index=False):
            yield Pulsar(*values)

    def by_name(
        self,
        name: str,
        regex: bool = False,
    ) -> pd.DataFrame:
        """Returns a DataFrame with records that match `name`.

        :param name: str
        :param regex: optional bool
        :return: pandas.DataFrame
        """
        return self.dataframe[self.dataframe.CNAME.str.contains(name, regex=regex)]

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
