"""a Pandas DataFrame loader for ATNF Pulsar Catalogue v1.64 data.
"""

import importlib.resources as ir

from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd

from loguru import logger


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
            return self._dataframe
        except Exception as error:
            logger.debug(f"{error} {self.csv_path}")

        pulsars = self.load_psrcat()

        self._dataframe = pd.DataFrame(data=list(pulsars.values()))

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

        return self._dataframe

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

        return pulsars

    def write(self, path: Union[str, Path] = None) -> None:
        """Save the contents of `dataframe` to `path`.

        If `path` is not specified, the path given when the
        catalog was created is used.

        :param path: Union[str, Path]
        """
        try:
            self.dataframe.to_csv(path)
        except Exception as error:
            logger.error(f"{error} {path}")
            raise
