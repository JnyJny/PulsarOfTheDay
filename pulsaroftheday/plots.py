"""
"""

from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from astropy import units
from loguru import logger

from astropy.coordinates import SkyCoord

from .catalog import ATNFPulsar as Pulsar

well_known_pulsars = pd.DataFrame(
    [
        ["Vela", 0.0893, 1.250 * 10 ** (-13), "orange"],
        ["Crab", 0.0334, 4.204 * 10 ** (-13), "green"],
        ["Geminga", 0.2371, 1.097 * 10 ** (-13), "purple"],
    ],
    columns=["NAME", "period", "pdot", "color"],
)


def generate_pdot_plot(df: pd.DataFrame, ax) -> None:

    df.plot.scatter(
        y="pdot",
        x="period",
        c="color",
        logx=True,
        logy=True,
        marker=".",
        ax=ax,
    )

    # Draw the lines denoting ages
    # see Handbook of Pulsar Astronmy, Lorimer & Kramer, Fig. 1.13

    p = np.logspace(-3, 1)
    suffix = ["00 kyr", " Myr", "0 Myr", "00 Myr", " Gyr", "0 Gyr"]
    for exponent, suffix in enumerate(suffix, 6):
        pdots = p / (2 * 10 ** exponent)
        ax.plot(p, pdots, "k--")
        ax.text(p[1], 4 * pdots[1], f"1{suffix}", rotation=20)


def generate_skymap_plot(df: pd.DataFrame, ax) -> None:

    pass


def generate_pdot_skymap_plots(
    df: pd.DataFrame,
    path: Union[str, Path],
    add_well_known_pulsars: bool = True,
) -> None:
    """"""

    path = Path(path).resolve()

    pdot_ax = plt.subplot(121)
    sky_ax = plt.subplot(122, projection="aitoff")

    if add_well_known_pulsars:
        df = well_known_pulsars.append(df)

    generate_pdot_plot(df, pdot_ax)

    generate_skymap_plot(df, sky_ax)

    logger.info(f"Saving figure to {path}.")
    plt.savefig(path)
    logger.debug(f"Figured saved.")

    return path
