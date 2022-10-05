import struct
import sys

from .telegram import TelegramInterface

UNICODE_SUPPORT = sys.stdout.encoding.lower().startswith("utf")


DEFAULT_PORT = "COM5"


class SuperK:

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
            print("\x1b[41mSOURCE TURNED OFF\x1b[0m")
            return False
        elif val == 2:
            print("\x1b[42mSOURCE TURNED ON\x1b[0m")
            return True

    def set_flux(self, value):
        if value < 0 or value > 100:
            raise ValueError(f"Flux value is limited between 0 and 100, got {value}")

        int_value = int(value * 10)
        # Output power setpoint 27h 0-1000 per-thousands in 16-bit unsigned int
        msg = struct.pack("<H", int_value)
        self.telegram.write(0x27, msg)
        self.get_flux()

    def get_flux(self):
        response = self.telegram.read(0x27)
        int_value = struct.unpack("<H", response[1])[0]
        value = int_value / 10
        print(f"Flux set to: {value}")
        print(flux_bar(value))
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
        code = self.INTERLOCK_STATUS[value]
        if msb == 0:
            print(f"\x1b[42mINTERLOCK: {code}\x1b[0m")
        else:
            print(f"\x1b[41mINTERLOCK: {code}\x1b[0m")
        return msb == 0

    def set_operation_mode(self, mode: int):
        if mode < 0 or mode > 2:
            raise ValueError(f"Operation mode should be 0, 1, or 2, got {mode}")
        msg = struct.pack("<B", mode)
        self.telegram.write(0x31, msg)
        self.get_operation_mode()

    def get_operation_mode(self):
        response = self.telegram.read(0x31)
        value = struct.unpack("<B", response[1])[0]
        code = self.OPERATION_MODE[value]
        print(f"MODE: {code}")
        return value

    def get_status_bits(self):
        response = self.telegram.read(0x66)
        return response[1]


def flux_bar(flux_value, width=40):
    frac = flux_value / 100
    num_fill = int(frac * width)
    rest = width - num_fill
    fill_char = "\u2588" if UNICODE_SUPPORT else "|"
    return f"{0} {fill_char * num_fill}{'-' * rest} {100}"
