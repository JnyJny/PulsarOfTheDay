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


def pprint_pulsar(pulsar: Pulsar) -> None:
    """Pretty print a pulsar to the console."""
    for n, line in enumerate(str(pulsar).splitlines()):
        fg = "black" if n else "green"
        typer.secho(line, fg=fg)


@cli.callback()
def main_command(
    ctx: typer.Context,
    verbose: int = typer.Option(0, "--verbose", "-v", count=True),
    path: Path = typer.Option(
        None, "--csv-path", "-p", help="Path to CSV format pulsar data."
    ),
) -> None:

    global catalog

    if not verbose:
        logger.disable("pulsaroftheday")
    else:

        logger.remove()
        logger_config = {
            "colorize": True,
            "format": "<green>{time}</green>|<level>{level:<8}</level>|{message}",
            "level": {1: "INFO", 2: "DEBUG", 3: "WARN"}.get(verbose, "INFO"),
        }
        logger.add(sys.stdout, **logger_config)

    try:

        csv_path = (Path(path or app_config_path) / "pulsars.csv").resolve()

        logger.info(f"Config path: {app_config_path}")

        catalog = PulsarCatalog(csv_path)

        logger.success(
            f"initialized catalog dataframe: {len(catalog.dataframe)} entries"
        )

        logger.info(f"Catalog data @ {catalog.csv_path.resolve()}")
        if not csv_path.exists():
            catalog.write()
            logger.info(f"Wrote CSV data to improve future startup times.")

    except Exception as error:
        logger.error(f"{error} on startup")
        typer.secho(f"{error} on startup", fg="red")
        raise typer.Exit()


def dump_pulsars(df: pd.DataFrame, keys: List[str] = None) -> None:
    """Dumps a CSV formated list of pulsars.

    :param df: pandas.DataFrame
    :param keys: optional List[str]
    """
    keys = keys or df.columns
    print(":".join(["INDEX"] + keys))
    for record in df[keys].itertuples(name="Pulsar_Dump"):
        print(":".join([str(f) for f in record]))


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
        help="Long listing of all pulsars in the catalog.",
    ),
    long_format: bool = typer.Option(
        False,
        "--long-format",
        "-l",
        is_flag=True,
        help="Print pulsar records with long CSV format.",
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
        typer.secho(
            "Error: --all and --pulsar are mutually exclusive options.", fg="red"
        )
        raise typer.Exit()

    if pulsar_name:
        # XXX print tweetable form of pulsar if possible/switch
        logger.info(f"Looking up {pulsar_name} in the catalog")
        df = catalog.dataframe[catalog.dataframe.NAME == pulsar_name]
        logger.info(f"Found {len(df)} matching records.")
        dump_pulsars(df)
        return

    if all_pulsars:
        logger.info(f"Listing {len(catalog.dataframe)} Pulsars")
        dump_pulsars(catalog.dataframe)
        return

    # Narrow the catalog to entries with only these keys
    df = catalog.dataframe[Pulsar.keys()].dropna()

    for record in df.itertuples(index=False, name="Pulsar"):
        try:
            pulsar = Pulsar(*record)
            pprint_pulsar(pulsar)
        except Exception as error:
            logger.error(f"{error} for record: {record}")
            raise


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

    df = catalog.dataframe.dropna(subset=["pdot"])

    logger.info(f"Pulsars in catalog matching critera: {len(df)}")

    sample = df.sample(100)

    if not pulsar_name:
        sample.loc[sample.index[0], "color"] = "green"
        pulsar = Pulsar(*sample[Pulsar.keys()].iloc[0].values)
    else:
        try:
            target = df[df.CNAME.str.contains(pulsar_name, regex=False)]

            logger.info(f"{pulsar_name} matched {len(target)} records")
            logger.info(f"{target}")
        except IndexError:
            typer.secho(
                f"Unable to locate '{pulsar_name}' in the catalog.",
                fg="red",
            )
            raise typer.Exit() from None

        pulsar = Pulsar(*target.iloc[0][Pulsar.keys()].values)
        sample = target.append(sample)

    if dryrun:
        logger.info(f"DRY RUN for {pulsar.NAME}")
        typer.secho(f"DRY RUN for {pulsar.NAME}", fg="yellow")

    pprint_pulsar(pulsar)

    # generate plot here

    plotfile = generate_pdot_skymap_plots(sample, plots_path / f"{today}.png")

    if not dryrun:
        logger.info(f"Preparing to tweet {pulsar.NAME}")

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        tweeter = tweepy.API(
            auth,
            wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True,
        )
        logger.info(f"Tweeting {plotfile} and {str(pulsar)}")
        try:
            tweet.update_with_media(filename=plotfile, status=str(pulsar))
        except Exception as error:
            logger.error(f"update_with_media failed: {error}")
            raise typer.Exit()
        logger.success(f"Tweeted {pulsar.NAME} @ {today}")

        # update the catalog with the date this pulsar was tweeted
        catalog.dataframe.loc[pulsar.NAME, "tweeted"] = today
        catalog.write()
        logger.info(f"Catalog updated @ {catalog.csv_path}")
    else:
        logger.info(f"DRY RUN COMPLETE: plot @ {plotfile}")
        typer.secho(f"DRY RUN COMPLETE: plot @ {plotfile}", fg="yellow")
