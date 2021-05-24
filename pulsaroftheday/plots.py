"""
"""

from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
import pandas as pd

from astropy import units
from loguru import logger

from .catalog import ATNFPulsar as Pulsar

well_known_pulsars = pd.DataFrame(
    [
        ["Vela", 0.0893, 1.250 * 10 ** (-13), "orange"],
        ["Crab", 0.0334, 4.204 * 10 ** (-13), "green"],
        ["Geminga", 0.2371, 1.097 * 10 ** (-13), "purple"],
    ],
    columns=["NAME", "period", "pdot", "color"],
)


def generate_plot(
    df: pd.DataFrame,
    path: Union[str, Path],
    add_well_known_pulsars: bool = True,
) -> None:
    """"""

    pdot_ax = plt.subplot(121)
    sky_ax = plt.subplot(122, projection="aitoff")

    if add_well_known_pulsars:
        df = well_known_pulsars.append(df)

    path = Path(path).resolve()

    df.plot.scatter(
        x="pdot",
        y="period",
        c="color",
        logx=True,
        logy=True,
        marker=".",
        ax=pdot_ax,
    )

    logger.info(f"Saving figure to {path}.")

    plt.savefig(path)

    logger.debug(f"Figured saved.")
