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
![CLI Screenshot][SCREENSHOT]
 
```console
2021-05-26T15:59:01.418384-0500|INFO    |Config path: /Users/ejo/Library/Application Support/PulsarOfTheDay
2021-05-26T15:59:01.452335-0500|SUCCESS |Pulsars in catalog: 2872
2021-05-26T15:59:01.455921-0500|SUCCESS |Plottable pulsars:  1133
2021-05-26T15:59:01.456079-0500|INFO    |Catalog data @ /Users/ejo/Library/Application Support/PulsarOfTheDay/pulsars.csv
2021-05-26T15:59:01.461082-0500|INFO    |Pulsars matching tweeting critera: 1133
2021-05-26T15:59:01.462164-0500|INFO    |DRY RUN for J1851-0053
2021-05-26T15:59:01.463260-0500|INFO    |RECORD B=nan J=J1851-0053
2021-05-26T15:59:01.463352-0500|PULSAR  |NAME: J1851-0053
2021-05-26T15:59:01.463392-0500|PULSAR  |PSRB: nan
2021-05-26T15:59:01.463421-0500|PULSAR  |PSRJ: J1851-0053
2021-05-26T15:59:01.463448-0500|PULSAR  |RAJ: 18:51:03.17
2021-05-26T15:59:01.463473-0500|PULSAR  |DECJ: -00:53:07.3
2021-05-26T15:59:01.463496-0500|PULSAR  |F0: 0.70969034698
2021-05-26T15:59:01.463520-0500|PULSAR  |F1: -4.4e-16
2021-05-26T15:59:01.463544-0500|PULSAR  |DM: 24.0
2021-05-26T15:59:01.813751-0500|DEBUG   |No wikipedia page for J1851-0053
2021-05-26T15:59:01.818610-0500|SUCCESS |Tweet text written to /Users/ejo/Library/Application Support/PulsarOfTheDay/tweets/2021-05-26.text
2021-05-26T15:59:01.926290-0500|INFO    |Generating p-pdot plot...
2021-05-26T15:59:01.957226-0500|DEBUG   |J1851-0053 8.736045358381725e-16 1.409065241277942 red
2021-05-26T15:59:01.958391-0500|DEBUG   |Vela 1.25e-13 0.0893 orange
2021-05-26T15:59:01.959520-0500|DEBUG   |Crab 4.204e-13 0.0334 green
2021-05-26T15:59:01.960629-0500|DEBUG   |Geminga 1.097e-13 0.2371 purple
2021-05-26T15:59:01.968854-0500|INFO    |Generating skymap plot...
2021-05-26T15:59:04.746698-0500|SUCCESS |Tweet plot written to /Users/ejo/Library/Application Support/PulsarOfTheDay/tweets/2021-05-26.png
2021-05-26T15:59:04.746828-0500|INFO    |DRY RUN COMPLETE, nothing tweeted.
```


[0]: https://twitter.com/PulsarOfTheDay
[1]: https://www.atnf.csiro.au/research/pulsar/psrcat/
[PLOT]: https://github.com/JnyJny/PulsarOfTheDay/blob/66534e05ba3bc54613f76451bf534646a0788f5a/example/2021-05-26.png

