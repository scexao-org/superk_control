import pytest

from superk_control.telegram import TelegramInterface, sub_special_chars, unsub_special_chars

TEST_DEST = b"\x0f"
TEST_SOURCE = b"\xa1"


class TestTelegram:

    def test_read(self, mock_serial):
        # test reading module name
        stub = mock_serial.stub(
            receive_bytes=b"\x0d" + TEST_DEST + TEST_SOURCE + b"\x0a"
        )

        telegram = TelegramInterface(port=mock_serial.port, dest=TEST_DEST, source=TEST_SOURCE)

        pass

    def test_write(self, mock_serial):
        pass

    def test_sub_special_letters(self):
        # page 15 SDK instruction manual
        test_bytes = b"\x0a\x42\x05\x32\x0d\x9c\xf0\x5e"
        test_bytes_subbed = b"\x5e\x4a\x42\x05\x32\x5e\x4d\x9c\xf0\x5e\x9e"

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

    