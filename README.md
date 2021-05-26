# The New & Improved Pulsar of The Day


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
$ git checkout jnyjny
$ poetry shell
<venv> $ poetry install
...
<venv> $ potd list
```

## Example Output

![J1846-0749](https://github.com/JnyJny/PulsarOfTheDay/blob/66534e05ba3bc54613f76451bf534646a0788f5a/example/2021-05-25T20:37:23.543529.png)

![CLI Screenshot](https://github.com/JnyJny/PulsarOfTheDay/blob/5343e883693d728d8b97b1cb2fdc63cee7dd6330/example/screenshot.png)

[example_png]: https://github.com/JnyJny/PulsarOfTheDay/blob/c1e596bfeceafa78a5ce57a510c82f942abcd474/example/2021-05-25T20:37:23.543529.png

[0]: https://twitter.com/PulsarOfTheDay
[1]: https://www.atnf.csiro.au/research/pulsar/psrcat/
