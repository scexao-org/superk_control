from serial import Serial

DEFAULT_PORT = ""


class SuperK:
    def __init__(self, port=DEFAULT_PORT, **serial_kwargs):
        self.port = port
        # from user manual: 115200/8/N/1
        self.serial = Serial(port=self.port, baudrate=115200, **serial_kwargs)

    def power_on(self):
        print("\x1b[42mSOURCE TURNED ON")
        # Emission 30h 8-bit unsigned int
        # 0 is off, 2 is on

    def power_off(self):
        print("\x1b[41mSOURCE TURNED OFF")
        # Emission 30h 8-bit unsigned int
        # 0 is off, 2 is on

    def set_flux(self, value):
        if value < 0 or value > 100:
            raise ValueError(f"Flux value is limited between 0 and 100, got {value}")

        # Output power setpoint 27h 0-1000 per-thousands in 16-bit unsigned int
        print(f"Flux set to: {value}")
        print(flux_bar(value))

    def get_flux(self):
        pass

    def get_interlock_status(self):
        # Interlock 32h
        pass

    def get_status(self):
        # Statsu bits 66h
        pass

    def send_telegram(self, msg):
        start_bit = 0x0D
        end_bit = 0x0A
        mod_address = 0  # 8Fh


def flux_bar(flux_value, width=40):
    frac = flux_value / 100
    num_fill = int(frac * width)
    rest = width - num_fill
    return f"{0} {'█' * num_fill}{'-' * rest} {100}"
