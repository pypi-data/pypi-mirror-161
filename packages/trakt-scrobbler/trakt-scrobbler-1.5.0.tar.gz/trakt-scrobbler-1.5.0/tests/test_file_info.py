import sys
import unittest
from unittest.mock import MagicMock, patch
sys.modules["trakt_scrobbler.notifier"] = MagicMock()
# sys.modules["trakt_scrobbler.config"] = MagicMock()
# sys.modules["confuse"] = MagicMock()
with patch("trakt_scrobbler.config"):
    from trakt_scrobbler.file_info import whitelist, whitelist_file
print(f"{whitelist!r}")


class TestWhitelisting(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def test_empty_list(self):
        res = whitelist_file("asdf")
        print(res)
