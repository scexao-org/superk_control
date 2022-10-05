from serial import Serial
from crc import CrcCalculator, Crc16
import struct


DEFAULT_PORT = ""

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
        0xff00: "Interlock circuit failure",
    }

    def __init__(self, port=DEFAULT_PORT, **serial_kwargs):
        self.telegram = TelegramInterface(port, dest=0x8F, **serial_kwargs)

    def power_on(self):
        # Emission 30h 8-bit unsigned int
        # 0 is off, 2 is on
        msg = struct.pack("<B", 2)
        self.telegram.write(0x30, msg)
        print("\x1b[42mSOURCE TURNED ON")

    def power_off(self):
        # Emission 30h 8-bit unsigned int
        # 0 is off, 2 is on
        msg = struct.pack("<B", 0)
        self.telegram.write(0x30, msg)
        print("\x1b[41mSOURCE TURNED OFF")

    def power_status(self):
        val = struct.unpack("<B", self.telegram.read(0x30))[0]
        if val == 0:
            print("\x1b[41mSOURCE TURNED OFF")
            return False
        elif val == 2:
            print("\x1b[42mSOURCE TURNED ON")
            return True


    def set_flux(self, value):
        if value < 0 or value > 100:
            raise ValueError(f"Flux value is limited between 0 and 100, got {value}")

        int_value = int(value * 10)
        # Output power setpoint 27h 0-1000 per-thousands in 16-bit unsigned int
        msg = struct.pack("<H", int_value)
        self.telegram.write(0x27, msg)

        print(f"Flux set to: {int_value / 10}")
        print(flux_bar(value / 10))

    def get_flux(self):
        int_value = struct.unpack("<H", self.telegram.read(0x27))[0]
        value = int_value / 10
        print(f"Flux set to: {value}")
        print(flux_bar(value))
        return value


    def get_interlock_status(self):
        status = struct.unpack("<B", self.telegram.read(0x32))[0]
        code = self.INTERLOCK_STATUS[status] 
        print(code)
        return code
        

class TelegramInterface:

    START_BIT = 0x0D
    END_BIT = 0x0A

    def __init__(self, port, dest, source=161, **serial_kwargs):
        self.port = port
        self.dest = dest
        if 160 < source and source < 256:
            self.source = source
        else:
            raise ValueError("source must be between 161 and 255")
        self.destsource = bytearray([self.dest, self.source])
        # from user manual: 115200/8/N/1
        self.serial = Serial(port=self.port, baudrate=115200, **serial_kwargs)
        self.crc_calculator = CrcCalculator(Crc16.CCITT, table_based=True)

    def read(self, register):
        msg = bytes([0x4, register])
        return self.send_telegram(msg)
        
    def write(self, register, message):
        msg = bytes([0x5, register, message])
        response = self.send_telegram(msg)
        return response


    def send_telegram(self, data: bytearray):
        msg = self.destsource.join(data)
        crc = self.crc_calculator.calculate_checksum(msg)
        crc_bits = struct.pack(">H", crc)
        payload = msg.join(crc_bits)
        self.sub_special_chars(payload)
        payload.insert(0, self.START_BIT)
        payload.append(self.END_BIT)
        print(f"raw payload: {payload}")
        payload_hex = payload.hex()
        print(f"payload bytes: {' '.join(a + b for a,b in zip(payload_hex[::2], payload_hex[1::2]))}")
        self.serial.write(payload)
        response = self.serial.read_until(self.END_BIT)
        print(f"raw response: {response}")
        response_hex = response.hex()
        print(f"response bytes: {' '.join(a + b for a,b in zip(response_hex[::2], response_hex[1::2]))}")
        # prune response
        response_msg = response.removeprefix(self.START_BIT).removesuffix(self.END_BIT)
        # replace special chars
        self.unsub_special_chars(response_msg)
        # check crc
        resp_crc = self.crc_calculator.calculate_checksum(response_msg)
        # assert resp_crc == 0
        print(f"response crc: {resp_crc}")
        del response_msg[-2:]
        # return data, if any
        response_type = response_data[2]
        if len(response_data) > 3:
            response_data = response_data[3:]
        else:
            response_data = b""

        return response_type, response_data
        


    def sub_special_chars(data: bytearray):
        # modifies data in place!!!
        i = 0
        N = len(data)
        while i < N:
            b = data[i]
            if b == 0x0a or b == 0x0d or b == 0x5e:
                data[i] = 0x5e
                data.insert(i + 1,  b + 0x40)
                i += 1
                N += 1
            i += 1

        return data

    def unsub_special_chars(data: bytearray):
        # modifies data in place!!!
        i = 0
        N = len(data)
        while i < N:
            b = data[i]
            if b == 0x5e:
                data[i] = data.pop(i + 1) - 0x40
                N -= 1
            i += 1

        return data

def flux_bar(flux_value, width=40):
    frac = flux_value / 100
    num_fill = int(frac * width)
    rest = width - num_fill
    return f"{0} {'█' * num_fill}{'-' * rest} {100}"


