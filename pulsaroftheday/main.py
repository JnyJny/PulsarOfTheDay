"""
"""
import os
import sys

from datetime import datetime
from pathlib import Path
from random import choice
from typing import Dict, List

import pandas as pd
import tweepy
import typer

from loguru import logger

from .catalogs import ATNFPulsarCatalog as PulsarCatalog


cli = typer.Typer()

catalog = None

app_config_path = Path(typer.get_app_dir("PulsarOfTheDay"))
app_config_path.mkdir(parents=True, exist_ok=True)

logger.level("PULSAR", no=38, color="<blue>", icon="✪")


def set_logging_level(level: int) -> None:

    logger.remove()

    logger_config = {
        "colorize": True,
        "format": "<green>{time}</green>|<level>{level:<8}</level>|{message}",
        "level": {
            0: "ERROR",
            1: "SUCCESS",
            2: "INFO",
            3: "DEBUG",
        }.get(level, "DEBUG"),
    }
    logger.add(sys.stdout, **logger_config)


@cli.callback()
def main_command(
    ctx: typer.Context,
    verbose: int = typer.Option(0, "--verbose", "-v", count=True),
    path: Path = typer.Option(
        None,
        "--csv-path",
        "-p",
        help="Path to CSV format pulsar data.",
    ),
) -> None:

    global catalog

    set_logging_level(verbose)

    try:
        csv_path = (Path(path or app_config_path) / "pulsars.csv").resolve()

        logger.info(f"Config path: {app_config_path}")

        catalog = PulsarCatalog(csv_path)

        logger.success(f"Pulsars in catalog: {len(catalog.dataframe)}")
        logger.success(f"Tweet-able pulsars: {len(catalog.tweetable)}")

        logger.info(f"Catalog data @ {catalog.csv_path.resolve()}")

        if not catalog.csv_path.exists():
            catalog.save()
            logger.info(f"Wrote CSV data to improve future startup times.")

    except Exception as error:
        logger.error(f"{error} on startup.")
        raise typer.Exit()


@cli.command(name="init")
def init_subcommand(
    ctx: typer.Context,
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        is_flag=True,
        help="Force re-initialize pulsar database from source data.",
    ),
) -> None:
    """Initialize the CSV database from the source database file."""

    set_logging_level(2)

    catalog.initialize(force=force)


@cli.command(name="list")
def list_subcommand(
    ctx: typer.Context,
    pulsar_name: str = typer.Option(
        None,
        "--pulsar-name",
        "-n",
        help="Either a B or J name for a given pulsar.",
    ),
    tweetable: bool = typer.Option(
        False,
        "--tweetable",
        "-t",
        help="List only tweetable pulsars.",
    ),
    full_dump: bool = typer.Option(
        False,
        "--long-listing",
        "-l",
        help="List all columns in the pulsar database.",
    ),
) -> None:
    """List pulsars in the catalog in CSV format."""

    df = catalog.tweetable if tweetable else catalog.dataframe

    if pulsar_name:
        df = catalog.by_name(pulsar_name)

    print(df.to_csv(index=True, index_label="INDEX"))


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
    tweet_archive_path: Path = typer.Option(
        None,
        "--tweet-archive-path",
        "-t",
        help="Path where tweet text and plots are written.",
    ),
    animated: bool = typer.Option(
        False,
        "--animate-plot",
        "-a",
        is_flag=True,
        help="Animate plots with approximate pulsar period.",
    ),
):
    """Tweet a pulsar record and accompanying plot."""

    if dryrun:
        logger.info(f"DRY RUN")

    tweets_path = Path(tweet_archive_path or app_config_path / "tweets").resolve()

    tweets_path.mkdir(parents=True, exist_ok=True)

    today = datetime.now().isoformat().partition("T")[0]

    tweet_plot = tweets_path / f"{today}.png"

    pulsar = catalog.plot_random_population(
        tweet_plot,
        include_name=pulsar_name,
        animated=animated,
    )

    logger.debug(f"Target pulsar: {pulsar.NAME}")

    logger.success(f"Tweet plot written to {tweet_plot}")

    tweet_path = tweets_path / f"{today}.text"

    tweet = catalog.tweet_text(pulsar.NAME)

    for line in tweet.splitlines():
        logger.log("PULSAR", line)

    try:
        tweet_path.write_text(tweet)
    except Exception as error:
        logger.error("f{error} writing tweet to {tweet_path}")
        raise typer.Exit()

    logger.success(f"Tweet text written to {tweet_path}")

    if dryrun:
        logger.info("DRY RUN COMPLETE, nothing tweeted.")
        return

    logger.info(f"Preparing to tweet {pulsar.NAME}")

    logger.info(f"Checking for twitter credentials...")
    try:
        for envvar in [
            "API_KEY",
            "API_SECRET_KEY",
            "ACCESS_TOKEN",
            "ACCESS_TOKEN_SECRET",
        ]:
            os.environ[envvar]
    except Exception as error:
        logger.error(f"{error}")
        raise typer.Exit() from None

    logger.success("Twitter credentials are available.")

    try:
        auth = tweepy.OAuthHandler(
            os.environ.get("API_KEY"),
            os.environ.get("API_SECRET_KEY"),
        )
    except Exception as error:
        logger.error(f"OAuthHandler {error}")
        raise typer.Exit() from None

    try:
        auth.set_access_token(
            os.environ.get("ACCESS_TOKEN"),
            os.environ.get("ACCESS_TOKEN_SECRET"),
        )
    except Exception as error:
        logger.error(f"set_access_token: {error}")
        raise typer.Exit() from None

    try:
        tweeter = tweepy.API(
            auth,
            wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True,
        )
    except Exception as error:
        logger.error(f"teepy.API {error}")
        raise typer.Exit() from None

    logger.info(f"Tweeting {pulsar.NAME} and {tweet_plot.name}")

    try:
        tweeter.update_with_media(filename=tweet_plot, status=tweet)
    except Exception as error:
        logger.error(f"update_with_media failed: {error}")
        raise typer.Exit()

    # update the catalog with the date this pulsar was tweeted

    catalog.mark_tweeted(pulsar.NAME, today)

    catalog.save()
    logger.debug(f"Catalog updated @ {catalog.csv_path}")

    logger.success(f"Tweeted {pulsar.NAME} @ {today}")
