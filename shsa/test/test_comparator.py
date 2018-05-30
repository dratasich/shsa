import unittest

from monitor.comparator import *
from monitor.fault import *


class ComparatorTestCase(unittest.TestCase):
    """Tests comparators."""

    def test_simple(self):
        c = SimpleComparator()
        # mismatches detected?
        mismatches, _ = c.compare([0, 0, 0, 1], 0.1)
        self.assertEqual(mismatches, [1, 1, 1, 3])
        # error applied?
        mismatches, _ = c.compare([0, 0, 0, 1], 1.1)
        self.assertEqual(mismatches, [0, 0, 0, 0])


class AgreementTestCase(unittest.TestCase):
    """Tests agreement protocol."""

    def test_agree(self):
        ok = ItomFaultStatusType.OK
        nok = ItomFaultStatusType.FAULTY
        undef = ItomFaultStatusType.UNDEFINED
        a = FaultAgreement()
        # all right
        status = a.agree([1.0, 1.0])
        self.assertEqual(status, [ok, ok])
        status = a.agree([1.0, 1.05, 1.0])
        self.assertEqual(status, [ok, ok, ok])
        status = a.agree([1.0, 1.05, 1.0, 0.98])
        self.assertEqual(status, [ok, ok, ok, ok])
        status = a.agree([1.0, 1.5, 1.9, 0.9], error=1.0)
        self.assertEqual(status, [ok, ok, ok, ok])
        # undefined
        status = a.agree([0, 2])
        self.assertEqual(status, [undef, undef])
        status = a.agree([None, 0, 2])
        self.assertEqual(status, [undef, undef, undef])
        status = a.agree([None, 0, 2, 4])
        self.assertEqual(status, [undef, undef, undef, undef])
        status = a.agree([0, 2, 4, 6])
        self.assertEqual(status, [undef, undef, undef, undef])
        status = a.agree([0, 2, 0, 2])
        self.assertEqual(status, [undef, undef, undef, undef])
        # 1-fault-tolerant
        status = a.agree([0, 2, 2])
        self.assertEqual(status, [nok, ok, ok])
        status = a.agree([0, 2, 2, 2])
        self.assertEqual(status, [nok, ok, ok, ok])
        status = a.agree([None, 2, 2, 2])
        self.assertEqual(status, [undef, ok, ok, ok])
        status = a.agree([None, 2, 2, 0])
        self.assertEqual(status, [undef, ok, ok, nok])


if __name__ == '__main__':
        unittest.main()
