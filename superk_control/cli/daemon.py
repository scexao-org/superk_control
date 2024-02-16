from argparse import ArgumentParser

from scxconf import IP_SC2, PYRONS3_HOST, PYRONS3_PORT
from swmain.infra.badsystemd.aux import auto_register_to_watchers
from swmain.network.pyroserver_registerable import PyroServer

from superk_control.superk import SuperK

parser = ArgumentParser(prog="superk_daemon", description="Launch the daemon for the SuperK source")


def main():
    parser.parse_args()
    auto_register_to_watchers("SC2_SUPERK", "SC2 SuperK PyRO")
    server = PyroServer(bindTo=(IP_SC2, 0), nsAddress=(PYRONS3_HOST, PYRONS3_PORT))
    ## create device objects
    print("Initializing devices")
    available = []
    key = "superk"
    try:
        device = SuperK.connect(local=True)
        ## Add to Pyro server
        globals()[key] = device
        server.add_device(device, device.PYRO_KEY, add_oneway_callables=True)
        print(f"- {key}: {device.PYRO_KEY}")
        available.append(key)
    except Exception:
        print(f" ! Failed to connect {key}")

    print("\nThe following variables are available in the shell:")
    print(", ".join(available))
    ## Start server
    server.start()


if __name__ == "__main__":
    main()
