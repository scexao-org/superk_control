import pytest
import sys

skipwindows = pytest.mark.skipif(sys.platform.startswith("win"), reason="MockSerial does not support Windows")