import struct
import os

from swmain.network.pyroclient import connect

from .telegram import TelegramInterface

DEFAULT_PORT = os.environ.get(
    "SUPERK_PORT",
    "/dev/serial/by-id/usb-Silicon_Labs_CP2102N_USB_to_UART_Bridge_Controller_9a3288b0d3e4ea11b72f84d5994a5d01-if00-port0",
)

INTERLOCK_STATUS = {
    0x0000: "Interlock off (interlock circuit open)",
    0x0001: "Waiting for interlock reset",
    0x0002: "Interlock is OK",
    0x1000: "Interlock power failure",
    0x2000: "Internal interlock",
    0x3000: "External Bus interlock",
    0x4000: "Door interlock",
    0x5000: "Key switch",
    0xFF00: "Interlock circuit failure",
}

OPERATION_MODE = {
    0: "Normal operation",
    1: "External enable activated",
    2: "External feedback activated",
}


class SuperK:
    PYRO_KEY = "SUPERK"

    def __init__(self, port=DEFAULT_PORT, **serial_kwargs):
        self.telegram = TelegramInterface(port, dest=0x0F, **serial_kwargs)

    def power_on(self):
        # Emission 30h 8-bit unsigned int
        # 0 is off, 2 is on
        msg = struct.pack("<B", 2)
        self.telegram.write(0x30, msg)
        self.power_status()

    def power_off(self):
        # Emission 30h 8-bit unsigned int
        # 0 is off, 2 is on
        msg = struct.pack("<B", 0)
        self.telegram.write(0x30, msg)
        self.power_status()

    def power_status(self):
        response = self.telegram.read(0x30)
        val = struct.unpack("<B", response[1])[0]
        if val == 0:
            return False
        elif val == 2:
            return True
        else:
            msg = f"Unrecognized power status value {val!r}"
            raise RuntimeError(msg)

    def set_flux(self, value):
        if value < 0 or value > 100:
            msg = f"Flux value is limited between 0 and 100, got {value}"
            raise ValueError(msg)
        # Output power setpoint 27h 0-1000 per-thousands in 16-bit unsigned int
        msg = struct.pack("<H", int(value * 10))
        self.telegram.write(0x27, msg)
        self.get_flux()

    def get_flux(self):
        response = self.telegram.read(0x27)
        int_value = struct.unpack("<H", response[1])[0]
        value = int_value / 10
        return value

    def reset_interlock(self):
        msg = struct.pack("<B", 1)
        self.telegram.write(0x32, msg)
        self.get_interlock_status()

    def disable_interlock(self):
        msg = struct.pack("<B", 0)
        self.telegram.write(0x32, msg)
        self.get_interlock_status()

    def get_interlock_status(self):
        response = self.telegram.read(0x32)
        msb = response[1][1]
        value = struct.unpack("<H", response[1])[0]
        code = INTERLOCK_STATUS[value]
        return msb, code

    def set_operation_mode(self, mode: int):
        if mode < 0 or mode > 2:
            raise ValueError(f"Operation mode should be 0, 1, or 2, got {mode}")
        msg = struct.pack("<B", mode)
        self.telegram.write(0x31, msg)
        self.get_operation_mode()

    def get_operation_mode(self):
        response = self.telegram.read(0x31)
        value = struct.unpack("<B", response[1])[0]
        code = OPERATION_MODE[value]
        return value, code

    def get_status_bits(self):
        response = self.telegram.read(0x66)
        return response[1]

    @classmethod
    def connect(__cls__, local: bool, pyro_key=None):
        if local:
            return __cls__()
        if pyro_key is None:
            pyro_key = __cls__.PYRO_KEY
        return connect(pyro_key)

    def update_keys(self, power=None, interlock=None, mode=None, flux=None):
        if power is None:
            power = self.power_status()

        if interlock is None:
            is_ok, interlock = self.get_interlock_status()

        if mode is None:
            mode_val, mode = self.get_operation_mode()

        if flux is None:
            flux = self.get_flux()

        if not is_ok:
            status = "INTERLOCK"
        else:
            status = "ON" if power else "OFF"

        ## TODO FITS header keys
        # update_keys(
        #     X_SRCST=status,
        #     X_SRCPW=flux,
        # )
