"""
"""

import sys

from datetime import datetime
from pathlib import Path
from random import choice
from typing import Dict, List

import pandas as pd
import tweepy
import typer

from loguru import logger

from .catalog import ATNFPulsarCatalog as PulsarCatalog
from .catalog import ATNFPulsar as Pulsar
from .plots import generate_pdot_skymap_plots

cli = typer.Typer()

catalog = None

app_config_path = Path(typer.get_app_dir("PulsarOfTheDay"))
app_config_path.mkdir(parents=True, exist_ok=True)


def log_pulsars(df: pd.DataFrame, dropna: bool = False) -> None:
    """Log a pulsar to the console."""

    pulsars = df[Pulsar.keys()].copy()

    if dropna:
        pulsars.dropna(inplace=True)

    for values in pulsars.itertuples(index=False):
        pulsar = Pulsar(*values)
        logger.info(f"RECORD B={pulsar.PSRB} J={pulsar.PSRJ}")
        for n, line in enumerate(str(pulsar).splitlines()):
            logger.log("PULSAR", line)


def dump_pulsars(df: pd.DataFrame, keys: List[str] = None) -> None:
    """Dumps a CSV formated list of pulsars.

    :param df: pandas.DataFrame
    :param keys: optional List[str]
    """
    keys = keys or df.columns
    keys.insert(0, "INDEX")
    print(":".join(keys))
    for record in df[keys].itertuples(name="Pulsar_Dump"):
        print(":".join([str(f) for f in record]))


@cli.callback()
def main_command(
    ctx: typer.Context,
    verbose: int = typer.Option(0, "--verbose", "-v", count=True),
    path: Path = typer.Option(
        None, "--csv-path", "-p", help="Path to CSV format pulsar data."
    ),
) -> None:

    global catalog

    logger.remove()
    logger_config = {
        "colorize": True,
        "format": "<green>{time}</green>|<level>{level:<8}</level>|{message}",
        "level": {1: "INFO", 2: "DEBUG"}.get(verbose, "INFO"),
    }
    logger.add(sys.stdout, **logger_config)
    logger.level("PULSAR", no=38, color="<blue>", icon="✪")

    try:

        csv_path = (Path(path or app_config_path) / "pulsars.csv").resolve()

        logger.info(f"Config path: {app_config_path}")

        catalog = PulsarCatalog(csv_path)

        logger.success(f"Pulsars in catalog: {len(catalog.dataframe)}")

        df = catalog.dataframe.dropna(subset=["RAJ", "DECJ", "period", "pdot"])

        logger.success(f"Good pulsar candidates: {len(df)}")

        logger.info(f"Catalog data @ {catalog.csv_path.resolve()}")

        if not csv_path.exists():
            catalog.write()
            logger.info(f"Wrote CSV data to improve future startup times.")

    except Exception as error:
        logger.error(f"{error} on startup")
        raise typer.Exit()


@cli.command(name="list")
def list_subcommand(
    ctx: typer.Context,
    pulsar_name: str = typer.Option(
        None, "--pulsar", "-p", help="Long listing for the named pulsar."
    ),
    all_pulsars: bool = typer.Option(
        False,
        "--all",
        "-a",
        is_flag=True,
        help="List all pulsars in the catalog.",
    ),
    long_listing: bool = typer.Option(
        False,
        "--long-fmt",
        "-l",
        help="List pulsars in CSV format.",
    ),
) -> None:
    """List pulsars in the catalog.

    By default, will list "tweetable" records which are those pulsar
    records with valid data for PSRB, PSRJ, RAJ, DECJ, F0, F1, and DM.

    When the user specifies --all, a long list in CSV format is printed
    to stdout for all records in the catalog.

    When the user specifies a specific pulsar with the `--pulsar` option,
    it will be printed in CSV format to stdout.
    """

    if all_pulsars and pulsar_name:
        logger.error("Mutually exclusive options: --all, --pulsar")
        raise typer.Exit()

    if pulsar_name:
        # XXX print tweetable form of pulsar if possible/switch
        logger.info(f"Looking up {pulsar_name} in the catalog")
        df = catalog.dataframe[catalog.dataframe.NAME == pulsar_name]
        logger.info(f"Found {len(df)} matching records.")
        log_pulsars(df)
        logger.success("List pulsar by name")
        return

    if all_pulsars:
        logger.info(f"Listing {len(catalog.dataframe)} Pulsars")
        dump_pulsars(catalog.dataframe)
        return

    # Narrow the catalog to entries with only these keys
    df = catalog.dataframe[Pulsar.keys()].dropna()

    if long_listing:
        dump_pulsars(df)
    else:
        log_pulsars(df)

    # for record in df.itertuples(index=False, name="Pulsar"):
    #     try:
    #         pulsar = Pulsar(*record)
    #         dump_pulsars(pulsar)
    #     except Exception as error:
    #         logger.error(f"{error} for record: {record}")
    #         raise


@cli.command(name="tweet")
def tweet_subcommand(
    ctx: typer.Context,
    dryrun: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        show_default=True,
        help="Do everything but tweet.",
    ),
    pulsar_name: str = typer.Option(
        None,
        "--pulsar",
        "-p",
        help="Specific pulsar name to tweet.",
    ),
    plots_path: Path = typer.Option(
        None,
        "--plots-path",
        "-P",
        help="Path to save generated plots.",
    ),
):
    """Tweet a pulsar record and accompanying plot."""

    plots_path = Path(plots_path or app_config_path / "plots").resolve()

    plots_path.mkdir(parents=True, exist_ok=True)

    today = datetime.now().isoformat()

    df = catalog.dataframe.dropna(subset=["period", "pdot", "DECJ", "RAJ"])

    logger.info(f"Pulsars matching critera: {len(df)}")

    sample = df.sample(len(df))  # random shuffle

    # If the user isn't requesting a particular pulsar by name,
    # we pick the first pulsar in `sample` as the "target" pulsar.
    #
    # When the user wants a particular pulsar, we search for it
    # and then append `sample` to "target" DataFrame and then
    # drop duplicates, keeping the first one. This shuffles the
    # target pulsar to top of the sample DataFrame without a duplicate.
    # The duplicate would just cause two draws of the pulsar in the
    # plotting phase, so it's not entirely necessary.

    if pulsar_name:
        target = df[df.CNAME.str.contains(pulsar_name, regex=False)]

        logger.info(f"{pulsar_name} matched {len(target)} records")

        if target.empty:
            logger.error(f"No pulsar matches '{pulsar_name}'")
            raise typer.Exit()

        sample = target.append(sample).drop_duplicates()

    # The first row in the dataframe is the target

    sample.loc[sample.index[0], "color"] = "red"
    pulsar = Pulsar(*sample.iloc[0][Pulsar.keys()].values)

    if dryrun:
        logger.info(f"DRY RUN for {pulsar.NAME}")

    log_pulsars(sample.head(1))

    plotfile = (plots_path / f"{today}.png").resolve()

    generate_pdot_skymap_plots(sample, plotfile)

    logger.success(f"Plot @ {plotfile}")

    if dryrun:
        logger.info("DRY RUN COMPLETE, nothing tweeted.")
        return

    logger.info(f"Preparing to tweet {pulsar.NAME}")

    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    except Exception as error:
        logger.error(f"OAuthHandler {error}")
        raise
    try:
        auth.set_access_token(access_token, access_token_secret)
    except Exception as error:
        logger.error(f"set_access_token: {error}")
        raise

    try:
        tweeter = tweepy.API(
            auth,
            wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True,
        )
    except Exception as error:
        logger.error(f"teepy.API {error}")

    logger.info(f"Tweeting {pulsar.NAME} and {plotfile}")

    try:
        tweet.update_with_media(filename=plotfile, status=str(pulsar))
    except Exception as error:
        logger.error(f"update_with_media failed: {error}")
        raise typer.Exit()

    # update the catalog with the date this pulsar was tweeted
    catalog.dataframe.loc[pulsar.NAME, "tweeted"] = today
    catalog.write()
    logger.debug(f"Catalog updated @ {catalog.csv_path}")

    logger.success(f"Tweeted {pulsar.NAME} @ {today}")
