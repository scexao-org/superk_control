#!/usr/bin/env python
from docopt import docopt
import sys

from ..superk import SuperK

__doc__ = """
Usage:
    superk -h | --help
    superk status
    superk power [on | off]
    superk flux [<value>]
    superk mode [<mode>]
    superk interlock [reset | disable]

Options:
    -h --help           Print this message

Commands:
    status              Print detailed status message
    power [on | off]    Turn source on or off (case insensitive). If no option provided, returns the power status.
    flux [<value>]      Change the intensity value of the source (0 to 100). If no value provided, return current flux
    mode [<mode>]       Change control mode between normal (0), external trigger (1) or external feedback (2). If no value provided return current mode
    interlock           Return interlock status
              reset     Try and reset interlock
              disable   Disable interlock (DANGEROUS)
"""
UNICODE_SUPPORT = sys.stdout.encoding.lower().startswith("utf")

def flux_bar(flux_value, width=40) -> str:
    frac = flux_value / 100
    num_fill = int(frac * width)
    rest = width - num_fill
    fill_char = "\u2588" if UNICODE_SUPPORT else "|"
    return f"0 |{fill_char * num_fill}{'-' * rest}| 100%"

def _power_status(superk: SuperK) -> None:
    status = superk.power_status()
    if status:
        print("\x1b[41mSOURCE TURNED ON\x1b[0m")
    else:
        print("\x1b[41mSOURCE TURNED OFF\x1b[0m")

def _flux_status(superk: SuperK) -> None:
    flux = superk.get_flux()
    print(f"Flux set to: {flux:.01f}%")
    print(flux_bar(flux))

def _mode_status(superk: SuperK) -> None:
    value, mode = superk.get_operation_mode()
    print(f"MODE: {mode} ({value})")

def _interlock_status(superk: SuperK) -> None:
    isok, code = superk.get_interlock_status()
    if isok:
        print(f"\x1b[41mINTERLOCK: {code}\x1b[0m")
    else:
        print(f"\x1b[42mINTERLOCK: {code}\x1b[0m")

def main() -> None:
    args = docopt(__doc__)

    superk = SuperK()

    # power
    if args["power"]:
        if args["on"]:
            superk.power_on()
        elif args["off"]:
            superk.power_off()
        _power_status(superk)
    # flux
    elif args["flux"]:
        if args["<value>"]:
            value = float(args["<value>"])
            superk.set_flux(value)
        _flux_status(superk)
    # mode
    elif args["mode"]:
        if args["<mode>"]:
            mode = int(args["<mode>"])
            superk.set_operation_mode(mode)
        _mode_status(superk)
    # interlock
    elif args["interlock"]:
        if args["reset"]:
            superk.reset_interlock()
        elif args["disable"]:
            superk.disable_interlock()
        _interlock_status(superk)
    # status
    elif args["status"]:
        _interlock_status(superk)
        _power_status(superk)
        _mode_status(superk)
        _flux_status(superk)
    else:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
