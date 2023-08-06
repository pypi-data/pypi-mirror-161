import unittest
from py7za import nice_size, size_to_int
from py7za._nice_size import SI_UNITS, BIN_UNITS


class TestWalker(unittest.TestCase):
    def test_nice_size_basic(self):
        self.assertEqual(nice_size(999, si=True), '999 B')
        self.assertEqual(nice_size(1000, si=True), '1.0 kB')
        self.assertEqual(nice_size(1023), '1023 B')
        self.assertEqual(nice_size(1024), '1.0 KiB')

    def test_nice_size_negative(self):
        self.assertEqual(nice_size(0), '0 B')
        self.assertEqual(nice_size(-1), '-1 B')
        self.assertEqual(nice_size(-999, si=True), '-999 B')
        self.assertEqual(nice_size(-1000, si=True), '-1.0 kB')
        self.assertEqual(nice_size(-1023), '-1023 B')
        self.assertEqual(nice_size(-1024), '-1.0 KiB')

    def test_nice_size_SI(self):
        for n, u in enumerate(SI_UNITS):
            self.assertEqual(nice_size(1000**(n+1), si=True), f'1.0 {u}')

    def test_nice_size_BIN(self):
        for n, u in enumerate(BIN_UNITS):
            self.assertEqual(nice_size(1024**(n+1)), f'1.0 {u}')

    def test_nice_size_roundtrip_bin(self):
        cases = [0, 990, 2048, 2**10, 999975760691]
        for c in cases:
            self.assertEqual(c, size_to_int(nice_size(c)))

    def test_nice_size_roundtrip_si(self):
        cases = [0, 990, 2000, 10**10]
        for c in cases:
            self.assertEqual(c, size_to_int(nice_size(c, si=True), si=True))
