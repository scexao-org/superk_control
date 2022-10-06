from superk_control.telegram import (
    TelegramInterface,
    sub_special_chars,
    unsub_special_chars,
)


def test_sub_special_chars():
    # special bytes include 0x0a, 0x0d, 0x5e
    # page 15 SDK instruction manual
    test_bytes = b"\x0A\x42\x05\x32\x0D\x9C\xF0\x5E"
    test_bytes_subbed = b"\x5E\x4A\x42\x05\x32\x5E\x4D\x9C\xF0\x5E\x9E"

    example_message = bytearray(test_bytes)
    subbed = sub_special_chars(example_message)

    # check value was changed in place
    assert bytes(example_message) != test_bytes
    assert bytes(subbed) == test_bytes_subbed

    # integration test
    unsubbed = unsub_special_chars(subbed)

    # check value was changed in place
    assert bytes(subbed) != test_bytes_subbed
    assert bytes(unsubbed) == test_bytes


class TestTelegram:
    def test_read(self, mock_serial):
        # test reading module name
        stub = mock_serial.stub(
            receive_bytes=b"\x0D\x0F\xA1\x04\x61\xEE\x01\x0A",
            send_bytes=b"\x0D\xA1\x0F\x08\x61\x8F\xA5\x06\x0A",
        )

        telegram = TelegramInterface(port=mock_serial.port, dest=0x0F, source=0xA1)

        flag, message = telegram.read(0x61)

        assert stub.called
        assert stub.calls == 1
        assert flag == 8
        assert (
            bytes(message) == b"\x8f"
        )  # expected module name for our SuperK EVO source

        telegram.serial.close()  # cleanup

    def test_write(self, mock_serial):
        # test writing to emission on register
        stub = mock_serial.stub(
            receive_bytes=b"\x0D\x0F\xA1\x05\x30\x02\x37\x1C\x0A",
            send_bytes=b"\x0D\xA1\x0F\x03\x30\xD3\xF3\x0A",
        )

        telegram = TelegramInterface(port=mock_serial.port, dest=0x0F, source=0xA1)

        flag, message = telegram.write(0x30, bytearray(b"\x02"))

        assert stub.called
        assert stub.calls == 1
        assert flag == 3
        assert bytes(message) == b""

        telegram.serial.close()  # cleanup
