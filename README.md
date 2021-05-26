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
[32m2021-05-26T15:59:01.418384-0500[0m|[1mINFO    [0m|Config path: /Users/ejo/Library/Application Support/PulsarOfTheDay
[32m2021-05-26T15:59:01.452335-0500[0m|[32m[1mSUCCESS [0m|Pulsars in catalog: 2872
[32m2021-05-26T15:59:01.455921-0500[0m|[32m[1mSUCCESS [0m|Plottable pulsars:  1133
[32m2021-05-26T15:59:01.456079-0500[0m|[1mINFO    [0m|Catalog data @ /Users/ejo/Library/Application Support/PulsarOfTheDay/pulsars.csv
[32m2021-05-26T15:59:01.461082-0500[0m|[1mINFO    [0m|Pulsars matching tweeting critera: 1133
[32m2021-05-26T15:59:01.462164-0500[0m|[1mINFO    [0m|DRY RUN for J1851-0053
[32m2021-05-26T15:59:01.463260-0500[0m|[1mINFO    [0m|RECORD B=nan J=J1851-0053
[32m2021-05-26T15:59:01.463352-0500[0m|[34mPULSAR  [0m|NAME: J1851-0053
[32m2021-05-26T15:59:01.463392-0500[0m|[34mPULSAR  [0m|PSRB: nan
[32m2021-05-26T15:59:01.463421-0500[0m|[34mPULSAR  [0m|PSRJ: J1851-0053
[32m2021-05-26T15:59:01.463448-0500[0m|[34mPULSAR  [0m|RAJ: 18:51:03.17
[32m2021-05-26T15:59:01.463473-0500[0m|[34mPULSAR  [0m|DECJ: -00:53:07.3
[32m2021-05-26T15:59:01.463496-0500[0m|[34mPULSAR  [0m|F0: 0.70969034698
[32m2021-05-26T15:59:01.463520-0500[0m|[34mPULSAR  [0m|F1: -4.4e-16
[32m2021-05-26T15:59:01.463544-0500[0m|[34mPULSAR  [0m|DM: 24.0
[32m2021-05-26T15:59:01.813751-0500[0m|[34m[1mDEBUG   [0m|No wikipedia page for J1851-0053
[32m2021-05-26T15:59:01.818610-0500[0m|[32m[1mSUCCESS [0m|Tweet text written to /Users/ejo/Library/Application Support/PulsarOfTheDay/tweets/2021-05-26.text
[32m2021-05-26T15:59:01.926290-0500[0m|[1mINFO    [0m|Generating p-pdot plot...
[32m2021-05-26T15:59:01.957226-0500[0m|[34m[1mDEBUG   [0m|J1851-0053 8.736045358381725e-16 1.409065241277942 red
[32m2021-05-26T15:59:01.958391-0500[0m|[34m[1mDEBUG   [0m|Vela 1.25e-13 0.0893 orange
[32m2021-05-26T15:59:01.959520-0500[0m|[34m[1mDEBUG   [0m|Crab 4.204e-13 0.0334 green
[32m2021-05-26T15:59:01.960629-0500[0m|[34m[1mDEBUG   [0m|Geminga 1.097e-13 0.2371 purple
[32m2021-05-26T15:59:01.968854-0500[0m|[1mINFO    [0m|Generating skymap plot...
[32m2021-05-26T15:59:04.746698-0500[0m|[32m[1mSUCCESS [0m|Tweet plot written to /Users/ejo/Library/Application Support/PulsarOfTheDay/tweets/2021-05-26.png
[32m2021-05-26T15:59:04.746828-0500[0m|[1mINFO    [0m|DRY RUN COMPLETE, nothing tweeted.
```


[0]: https://twitter.com/PulsarOfTheDay
[1]: https://www.atnf.csiro.au/research/pulsar/psrcat/
[PLOT]: https://github.com/JnyJny/PulsarOfTheDay/blob/66534e05ba3bc54613f76451bf534646a0788f5a/example/2021-05-26.png

