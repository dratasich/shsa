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
        itoms = {'i_m': 0.0, 'i_s': 0.0, 'i_n': 0.0, 'i_p': [0, 0, 0], 'i_t':
                 0.0}
        exp_status = {'i_m': ItomFaultStatusType.OK, 'i_s':
                      ItomFaultStatusType.OK, 'i_n': ItomFaultStatusType.OK,
                      'i_p': ItomFaultStatusType.OK, 'i_t':
                      ItomFaultStatusType.OK}
        rec_status = m.monitor(itoms)
        self.assertEqual(rec_status, exp_status)
        itoms = {'i_m': 1.0, 'i_s': 0.0, 'i_n': 0.0, 'i_p': [0, 0, 0], 'i_t':
                 0.0}
        exp_status = {'i_m': ItomFaultStatusType.FAULTY, 'i_s':
                      ItomFaultStatusType.OK, 'i_n': ItomFaultStatusType.OK,
                      'i_p': ItomFaultStatusType.FAULTY, 'i_t':
                      ItomFaultStatusType.OK}
        rec_status = m.monitor(itoms)
        self.assertEqual(rec_status, exp_status)


if __name__ == '__main__':
        unittest.main()
