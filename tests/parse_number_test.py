import unittest
from src.utils.log_utils import parse_int
from src.utils.log_utils import parse_float


class TestLogParser(unittest.TestCase):
    
    def test_parse_int(self):
        assert parse_int("123") == 123
        assert parse_int("  1234   ") == 1234
        assert parse_int("456 bytes") == 456
        assert parse_int("789 MB") == 789
        assert parse_int("10 files") == 10
        assert parse_int("asdf 10 files") == 10
        assert parse_int("20 files 2000") == 20
        assert parse_int("0 files") == 0
        assert parse_int("123.12 asdf") == 123
        assert parse_int(" asdf") is None
        assert parse_int(" ") is None
        assert parse_int("") is None
        assert parse_int(None) is None

    def test_parse_float(self):
        assert parse_float("123.45") == 123.45
        assert parse_float("  1234.45   ") == 1234.45
        assert parse_float("678.90 ms") == 678.90
        assert parse_float("3009 ms") == 3009.00
        assert parse_float("asdf 3009 ms") == 3009.00
        assert parse_float("120 ms 9999") == 120.00
        assert parse_float("0 ms") == 0.00
        assert parse_float(" ms") == None
        assert parse_float("") is None
        assert parse_float(None) is None

if __name__ == '__main__':
    unittest.main()