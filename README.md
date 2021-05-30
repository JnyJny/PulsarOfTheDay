# The Pulsar of The Day Twitter Bot

This repository houses the code for the [Twitter bot][0] of the same
name. It's designed to randomly pick a pulsar from the [ATNF pulsar
catalog][1] and tweet out information about it - period, dispersion
measure, characteristic age, etc. The bot also generates a couple of
plots: a P-Pdot diagram and a skymap in galactic coordinates, both
containing the chosen pulsar and a selection of other pulsars.


## Install

``` console
$ python3 -m pip install git+https://github.com/JnyJny/PulsarOfTheDay.git
$ potd --help
```

## Usage

### Overall Help
``` console
$ potd --help
Usage: potd [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose                   [default: 0]
  -p, --csv-path PATH             Path to CSV format pulsar data.
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.

Commands:
  init
  list   List pulsars in the catalog in CSV format.
  tweet  Tweet a pulsar record and accompanying plot.
```

### init Subcommand

```
$ potd init --help
Usage: potd init [OPTIONS]

  Initialize the CSV database from the source database file.

Options:
  -f, --force  Force re-initialize pulsar database from source data.
               [default: False]

  --help       Show this message and exit.
```

### list Subcommand
```
$ potd list --help
Usage: potd list [OPTIONS]

  List pulsars in the catalog in CSV format.

Options:
  -n, --pulsar-name TEXT  Either a B or J name for a given pulsar.
  -p, --plottable         List only plottable pulsars.  [default: False]
  -l, --long-listing      List all columns in the pulsar database.  [default:
                          False]

  --help                  Show this message and exit.
```

### tweet Subcommand
```
$ potd tweet --help
Usage: potd tweet [OPTIONS]

  Tweet a pulsar record and accompanying plot.

Options:
  -n, --dry-run                  Do everything but tweet.  [default: False]
  -p, --pulsar TEXT              Specific pulsar name to tweet.
  -t, --tweet-archive-path PATH  Path where tweet text and plots are written.
  --help                         Show this message and exit.
```

## Development

```console
$ python3 -m pip install poetry
$ git clone https://github.com/JnyJny/PulsarOfTheDay.git
$ cd PulsarOfTheDay
$ poetry shell
<venv> $ poetry install
...
<venv> $ potd list
```

## Example Output

![J1846-0749][PLOT]

### Twitter Status Text
```
Pulsar: J1901+0124
RA: 19:01:52.545
Dec: +01:24:49.3
Period: 0.319 s
Pdot: 3.241e-15
DM: 314.4 pc/cm^3
Characteristic Age: 4.918e+13 yr
Surface Magnetic Field: 1.017e+12 G
Visible from Arecibo, CHIME, FAST, GBT, VLA
```

### Command Output with verbosity turned up.
```console
$ potd -vvv twitter -n
2021-05-30T18:04:14.748392-0500|INFO    |Config path: /Users/ejo/Library/Application Support/PulsarOfTheDay
2021-05-30T18:04:14.779844-0500|SUCCESS |Pulsars in catalog: 2872
2021-05-30T18:04:14.782457-0500|SUCCESS |Tweet-able pulsars: 1133
2021-05-30T18:04:14.783131-0500|INFO    |Catalog data @ /Users/ejo/Library/Application Support/PulsarOfTheDay/pulsars.csv
2021-05-30T18:04:14.787687-0500|INFO    |Matched 1 records for J1901+0124
2021-05-30T18:04:14.809762-0500|INFO    |Pulsars matching tweeting critera: 1133
2021-05-30T18:04:14.810297-0500|INFO    |DRY RUN for J1901+0124
2021-05-30T18:04:14.812870-0500|PULSAR  |Pulsar: J1901+0124
2021-05-30T18:04:14.812955-0500|PULSAR  |RA: 19:01:52.545
2021-05-30T18:04:14.812987-0500|PULSAR  |Dec: +01:24:49.3
2021-05-30T18:04:14.813013-0500|PULSAR  |Period: 0.319 s
2021-05-30T18:04:14.813036-0500|PULSAR  |Pdot: 3.241e-15
2021-05-30T18:04:14.813059-0500|PULSAR  |DM: 314.4 pc/cm^3
2021-05-30T18:04:14.813081-0500|PULSAR  |Characteristic Age: 4.918e+13 yr
2021-05-30T18:04:14.813104-0500|PULSAR  |Surface Magnetic Field: 1.017e+12 G
2021-05-30T18:04:14.813126-0500|PULSAR  |Visible from Arecibo, CHIME, FAST, GBT, VLA
2021-05-30T18:04:14.813541-0500|SUCCESS |Tweet text written to /Users/ejo/Library/Application Support/PulsarOfTheDay/tweets/2021-05-30.text
2021-05-30T18:04:14.936695-0500|INFO    |Generating p-pdot plot...
2021-05-30T18:04:14.972144-0500|DEBUG   |J1901+0124 3.2414413462623512e-15 0.31881725933498317 red
2021-05-30T18:04:14.973481-0500|DEBUG   |Vela 1.25e-13 0.0893 orange
2021-05-30T18:04:14.974827-0500|DEBUG   |Crab 4.204e-13 0.0334 green
2021-05-30T18:04:14.976001-0500|DEBUG   |Geminga 1.097e-13 0.2371 purple
2021-05-30T18:04:14.985914-0500|INFO    |Generating skymap plot...
2021-05-30T18:04:15.509827-0500|DEBUG   |Origins: [[404, 276], [900, 346]]
2021-05-30T18:04:15.509933-0500|DEBUG   |period 0.31881725933498317 nframes 9 duration=0.03542413992610924
2021-05-30T18:04:15.586470-0500|DEBUG   |Number of frames: 9
2021-05-30T18:04:15.745957-0500|SUCCESS |Tweet plot written to /Users/ejo/Library/Application Support/PulsarOfTheDay/tweets/2021-05-30.png
2021-05-30T18:04:15.847898-0500|INFO    |Catalog updated @ /Users/ejo/Library/Application Support/PulsarOfTheDay/pulsars.csv
2021-05-30T18:04:15.848010-0500|INFO    |DRY RUN COMPLETE, nothing tweeted.
```


[0]: https://twitter.com/PulsarOfTheDay
[1]: https://www.atnf.csiro.au/research/pulsar/psrcat/
[PLOT]: https://github.com/JnyJny/PulsarOfTheDay/blob/0c1e49def984db4f11bd69249f980a828d4e74fd/example/example.png
