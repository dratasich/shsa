import unittest

from monitor.shsamonitor import SHSAMonitor
from monitor.fault import ItomFaultStatusType
from model.shsamodel import SHSAModel


class SHSAMonitorTestCase(unittest.TestCase):
    """Tests SHSA monitor."""

    def setUp(self):
        self.__domain = "s"
        self.__model = SHSAModel(configfile="test/model_m1.yaml")

    def tearDown(self):
        self.__domain = None
        self.__model = None

    def test_setup_monitor(self):
        m = SHSAMonitor(model=self.__model, domain=self.__domain)
        self.assertEqual(self.__model, m.model,
                         "model initialization failed")
        self.assertEqual(self.__domain, m.domain,
                         "domain initialization failed")

    def test_monitor(self):
        m = SHSAMonitor(model=self.__model, domain=self.__domain)
        itoms = {'/s/measurement': 0.0, '/s/detection': 0.0, '/n/detection':
                 0.0, '/s/pose': [0, 0, 0], '/clock': 0.0}
        exp_status = {'/s/measurement': ItomFaultStatusType.OK, '/s/detection':
                      ItomFaultStatusType.OK, '/n/detection':
                      ItomFaultStatusType.OK, '/s/pose':
                      ItomFaultStatusType.OK, '/clock': ItomFaultStatusType.OK}
        rec_status = m.monitor(itoms)
        self.assertEqual(rec_status, exp_status)
        itoms = {'/s/measurement': 1.0, '/s/detection': 0.0, '/n/detection':
                 0.0, '/s/pose': [0, 0, 0], '/clock': 0.0}
        exp_status = {'/s/measurement': ItomFaultStatusType.FAULTY,
                      '/s/detection': ItomFaultStatusType.OK, '/n/detection':
                      ItomFaultStatusType.OK, '/s/pose':
                      ItomFaultStatusType.FAULTY, '/clock':
                      ItomFaultStatusType.OK}
        rec_status = m.monitor(itoms)
        self.assertEqual(rec_status, exp_status)


if __name__ == '__main__':
        unittest.main()
