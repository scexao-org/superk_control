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
    superk filter [<pos>]
    superk mode [<mode>]
    superk interlock [reset | disable]

Options:
    -h --help           Print this message

Commands:
    status              Print detailed status message
    power [on | off]    Turn source on or off (case insensitive). If no option provided, returns the power status.
    flux [<value>]      Change the intensity value of the source (0 to 100). If no value provided, return current flux
    filter [<pos>]      (INACTIVE) Change the ND filter in the source
    mode [<mode>]       Change control mode between normal (0), external trigger (1) or external feedback (2). If no value provided return current mode
    interlock           Return interlock status
              reset     Try and reset interlock
              disable   Disable interlock (DANGEROUS)

    
"""


def main():
    args = docopt(__doc__)

    superk = SuperK()

    if args["power"]:
        if args["on"]:
            superk.power_on()
        elif args["off"]:
            superk.power_off()
        else:
            superk.power_status()
    elif args["flux"]:
        if args["<value>"]:
            value = float(args["<value>"])
            superk.set_flux(value)
        else:
            superk.get_flux()
    elif args["filter"]:
        print(f"No filter options yet")
        sys.exit(1)
    elif args["mode"]:
        if args["<mode>"]:
            mode = int(args["<mode>"])
            superk.set_operation_mode(mode)
        else:
            superk.get_operation_mode()
    elif args["interlock"]:
        if args["reset"]:
            superk.reset_interlock()
        elif args["disable"]:
            superk.disable_interlock()
        else:
            superk.get_interlock_status()
    else:
        superk.get_interlock_status()
        superk.power_status()
        superk.get_operation_mode()
        superk.get_flux()
    sys.exit(0)

if __name__ == "__main__":
    main()
