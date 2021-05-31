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

![J1743-3153][PLOT]

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
$ potd -vvv twitter -n -a
2021-05-31T16:35:48.297670-0500|INFO    |Config path: /Users/ejo/Library/Application Support/PulsarOfTheDay
2021-05-31T16:35:48.327344-0500|SUCCESS |Pulsars in catalog: 2872
2021-05-31T16:35:48.332917-0500|SUCCESS |Tweet-able pulsars: 1133
2021-05-31T16:35:48.333104-0500|INFO    |Catalog data @ /Users/ejo/Library/Application Support/PulsarOfTheDay/pulsars.csv
2021-05-31T16:35:48.333363-0500|INFO    |DRY RUN
2021-05-31T16:35:48.336808-0500|INFO    |Matched 1 records for J1743-3153
2021-05-31T16:35:48.459893-0500|INFO    |Generating p-pdot plot...
2021-05-31T16:35:48.492165-0500|DEBUG   |J1743-3153 1.056745222351872e-14 0.19310539993210338 red
2021-05-31T16:35:48.493139-0500|DEBUG   |Vela 1.25e-13 0.0893 orange
2021-05-31T16:35:48.494377-0500|DEBUG   |Crab 4.204e-13 0.0334 green
2021-05-31T16:35:48.495478-0500|DEBUG   |Geminga 1.097e-13 0.2371 purple
2021-05-31T16:35:48.503714-0500|INFO    |Generating skymap plot...
2021-05-31T16:35:48.525886-0500|DEBUG   |Target name J1743-3153
2021-05-31T16:35:48.540480-0500|INFO    |Plots generated
2021-05-31T16:35:48.994951-0500|DEBUG   |Origins: [(858, 348)]
2021-05-31T16:35:48.995071-0500|DEBUG   |period 0.19310539993210338 nframes 2 duration=0.02
2021-05-31T16:35:49.081575-0500|DEBUG   |Target pulsar: J1743-3153
2021-05-31T16:35:49.081699-0500|SUCCESS |Tweet plot written to /Users/ejo/Library/Application Support/PulsarOfTheDay/tweets/2021-05-31.png
2021-05-31T16:35:49.084079-0500|DEBUG   |J1743-3153 in  1133 records?
2021-05-31T16:35:49.084970-0500|INFO    |Matched 1 records for J1743-3153
2021-05-31T16:35:49.087284-0500|PULSAR  |Pulsar: J1743-3153
2021-05-31T16:35:49.087370-0500|PULSAR  |RA: 17:43:15.565
2021-05-31T16:35:49.087408-0500|PULSAR  |Dec: -31:53:05.3
2021-05-31T16:35:49.087446-0500|PULSAR  |Period: 0.193 s
2021-05-31T16:35:49.087474-0500|PULSAR  |Pdot: 1.057e-14
2021-05-31T16:35:49.087502-0500|PULSAR  |DM: 505.7 pc/cm^3
2021-05-31T16:35:49.087528-0500|PULSAR  |Characteristic Age: 9.137e+12 yr
2021-05-31T16:35:49.087555-0500|PULSAR  |Surface Magnetic Field: 1.429e+12 G
2021-05-31T16:35:49.087581-0500|PULSAR  |Visible from GBT, VLA
2021-05-31T16:35:49.087961-0500|SUCCESS |Tweet text written to /Users/ejo/Library/Application Support/PulsarOfTheDay/tweets/2021-05-31.text
2021-05-31T16:35:49.088020-0500|INFO    |DRY RUN COMPLETE, nothing tweeted.
```


[0]: https://twitter.com/PulsarOfTheDay
[1]: https://www.atnf.csiro.au/research/pulsar/psrcat/
[PLOT]: https://github.com/JnyJny/PulsarOfTheDay/blob/master/example/example.png
