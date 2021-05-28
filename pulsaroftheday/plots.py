"""
"""

from pathlib import Path
from typing import Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from astropy import units
from loguru import logger

from astropy import units as u
from astropy.coordinates import SkyCoord

well_known_pulsars = pd.DataFrame(
    [
        ["Vela", 0.0893, 1.250 * 10 ** (-13), "orange"],
        ["Crab", 0.0334, 4.204 * 10 ** (-13), "green"],
        ["Geminga", 0.2371, 1.097 * 10 ** (-13), "purple"],
    ],
    columns=["NAME", "period", "pdot", "color"],
)


def generate_pdot_plot(
    df: pd.DataFrame,
    ax,
    include_well_known_pulsars: bool = True,
) -> None:

    named_pulsars = df.head(1).copy()

    if include_well_known_pulsars:
        named_pulsars = named_pulsars.append(well_known_pulsars)

    df.tail(-1).plot.scatter(
        y="pdot",
        x="period",
        c="color",
        marker=".",
        ax=ax,
    )

    for p in named_pulsars.itertuples():
        logger.debug(f"{p.NAME} {p.pdot} {p.period} {p.color}")
        ax.scatter([p.period], [p.pdot], c=p.color, marker="o", label=p.NAME)

    # Draw the lines denoting ages
    # see Handbook of Pulsar Astronmy, Lorimer & Kramer, Fig. 1.13

    p = np.logspace(-3, 1)
    suffix = ["00 kyr", " Myr", "0 Myr", "00 Myr", " Gyr", "0 Gyr"]
    for exponent, suffix in enumerate(suffix, 5):
        age = (10 ** exponent * units.yr).to(units.s).value
        pdots = p / (2 * age)
        ax.plot(p, pdots, "k--", alpha=0.2)
        ax.text(p[1], 4 * pdots[1], f"1{suffix}", rotation=20, alpha=0.2)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(10 ** -3, 10)
    ax.set_ylim(10 ** -22, 10 ** -10)
    ax.set_xlabel("Period (s)")
    ax.set_ylabel("Period derivative (s s$^{-1}$)")
    ax.legend()


def generate_skymap_plot(df: pd.DataFrame, ax) -> None:
    """"""

    df.tail(-1).plot.scatter(
        x="g_lat",
        y="g_long",
        c="color",
        marker=".",
        ax=ax,
    )

    label = df.NAME[0]

    df.head(1).plot.scatter(
        x="g_lat",
        y="g_long",
        c="color",
        marker="o",
        label=label,
        ax=ax,
    )
    ax.grid()
    ax.legend()


def generate_pdot_skymap_plots(
    df: pd.DataFrame,
    path: Union[str, Path],
    include_well_known_pulsars: bool = True,
    figsize: Tuple[float, float] = None,
) -> None:
    """"""

    path = Path(path).resolve()

    figsize = figsize or (12.0, 7.0)

    pdot_ax = plt.subplot(121)
    sky_ax = plt.subplot(122, projection="aitoff")

    df.loc[df.index[0], "color"] = "red"

    logger.info(f"Generating p-pdot plot...")
    generate_pdot_plot(df, pdot_ax, include_well_known_pulsars)

    logger.info(f"Generating skymap plot...")
    generate_skymap_plot(df, sky_ax)

    plt.gcf().set_size_inches(figsize)
    plt.savefig(path)
