import unittest

from monitor.comparator import *


class ComparatorTestCase(unittest.TestCase):
    """Tests comparators."""

    def test_simple(self):
        c = SimpleComparator()
        # mismatches detected?
        mismatches = c.compare([0, 0, 0, 1], 0.1)
        self.assertEqual(mismatches, [1, 1, 1, 3])
        # error applied?
        mismatches = c.compare([0, 0, 0, 1], 1.1)
        self.assertEqual(mismatches, [0, 0, 0, 0])


if __name__ == '__main__':
        unittest.main()
