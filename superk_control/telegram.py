from crc import CrcCalculator, Crc16
import logging
from serial import Serial
import struct


class TelegramInterface:

    START_BIT = b"\x0D"
    END_BIT = b"\x0A"

    RESPONSE_TABLE = {
        0: "Message not understood, not applicable, or not allowed",
        1: "CRC error in received message",
        2: "Cannot respond at the moment. Module too busy",
        3: "Received message understood",
    }

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
        self.logger = logging.getLogger(__class__.__name__)

    def read(self, register):
        msg = bytearray([0x4, register])
        response = self.send_telegram(msg)
        if response[0] != 8:
            raise RuntimeError(self.RESPONSE_TABLE[response[0]])
        return response

    def write(self, register, message: bytearray):
        msg = bytearray([0x5, register]) + message
        response = self.send_telegram(msg)
        if response[0] != 3:
            raise RuntimeError(self.RESPONSE_TABLE[response[0]])
        return response

    def send_telegram(self, data: bytearray):
        # craft variable parts of message
        msg = self.destsource + data
        # calculate CRC checksum and append to message
        crc = self.crc_calculator.calculate_checksum(msg)
        payload = msg + struct.pack(">H", crc)
        # substitute special chars with substitute bytes
        sub_special_chars(payload)

        payload_hex = payload.hex()
        self.logger.debug(
            f"payload bytes: {' '.join(a + b for a,b in zip(payload_hex[::2], payload_hex[1::2]))}"
        )

        # framing
        payload = self.START_BIT + payload + self.END_BIT

        # write serial
        self.serial.write(payload)
        # don't start reading until SOT
        self.serial.read_until(self.START_BIT)
        # read until EOT, throw out EOT bit
        response_msg = bytearray(self.serial.read_until(self.END_BIT))[:-1]

        response_hex = response_msg.hex()
        self.logger.debug(
            f"response bytes: {' '.join(a + b for a,b in zip(response_hex[::2], response_hex[1::2]))}"
        )

        # replace substituted bytes with special chars
        unsub_special_chars(response_msg)
        # check crc, should be 0
        resp_crc = self.crc_calculator.calculate_checksum(response_msg)
        self.logger.debug(f"response crc: {resp_crc}")
        assert resp_crc == 0, f"response CRC was not 0"

        # return type, return data if any, skipping CRC bytes
        response_type = response_msg[2]
        response_data = response_msg[4:-2]

        return response_type, response_data


def sub_special_chars(data: bytearray):
    # modifies data in place!!!
    i = 0
    N = len(data)
    while i < N:
        b = data[i]
        if b == 0x0A or b == 0x0D or b == 0x5E:
            data[i] = 0x5E
            data.insert(i + 1, b + 0x40)
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
        if b == 0x5E:
            data[i] = data.pop(i + 1) - 0x40
            N -= 1
        i += 1

    return data
