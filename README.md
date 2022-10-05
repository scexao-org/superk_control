# superk_control

Control software for NKT Photonics SuperK EVO lasers

## Installation

Clone this repository and pip-install it however you like

```
$ pip install git+https://github.com/scexao-org/superk_control#egg=superk_control
```

## Setup

Set the `SUPERK_PORT` environment variable to the serial port for communication (e.g., "COM5", "/dev/ttyUSB3")

```
$ export SUPERK_PORT="COM5"
```

## Usage

The `superk` script is the entrypoint for all instrument control. The rest of the API can be found from the methods defined in the `superk.py` class.

```
$ superk --help
Usage:
    superk -h | --help
    superk status
    superk power [on | off]
    superk flux [<value>]
    superk filter <pos>
    superk mode [<mode>]
    superk interlock [reset | disable]

Options:
    -h --help           Print this message

Commands:
    status              Print detailed status message
    power [on | off]    Turn source on or off (case insensitive). If no option provided, returns the power status.
    flux [<value>]      Change the intensity value of the source (0 to 100). If no value provided, return current flux
    filter <pos>        (INACTIVE) Change the ND filter in the source
    mode [<mode>]       Change control mode between normal (0), external trigger (1) or external feedback (2). If no value provided return current mode
    interlock           Return interlock status
              reset     Try and reset interlock
              disable   Disable interlock (DANGEROUS)
```
