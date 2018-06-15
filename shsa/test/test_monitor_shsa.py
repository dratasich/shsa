import unittest
import yaml

from monitor.shsamonitor import SHSAMonitor
from monitor.fault import ItomFaultStatusType
from model.shsamodel import SHSAModel


class SHSAMonitorTestCase(unittest.TestCase):
    """Tests SHSA monitor."""

    def setUp(self):
        self.__domain = "a"
        self.__model = SHSAModel(configfile="test/model_e1.yaml")

    def tearDown(self):
        self.__domain = None
        self.__model = None

    def test_setup_monitor(self):
        m = SHSAMonitor(model=self.__model, domain=self.__domain)
        self.assertEqual(self.__model, m.model,
                         "model initialization failed")
        self.assertEqual(self.__domain, m.domain,
                         "domain initialization failed")
        self.assertEqual(None, m.itoms)
        itoms_available_for_monitor = ['i_a', 'i_d']
        m.itoms = itoms_available_for_monitor
        self.assertEqual(itoms_available_for_monitor, m.itoms,
                         "itoms initialization failed")

    def test_monitor(self):
        """Test 1-fault-tolerance."""
        m = SHSAMonitor(model=self.__model, domain=self.__domain)
        itoms = {'i_a': 0, 'i_d': 0, 'i_e': 0, 'i_f': 0}
        exp_status = {itom: ItomFaultStatusType.OK for itom in itoms}
        ret_status = m.monitor(itoms)
        self.assertEqual(ret_status, exp_status, "wrong fault status")
        itoms = {'i_a': 0, 'i_d': 0, 'i_e': 0, 'i_f': 1}
        exp_status = {itom: ItomFaultStatusType.OK for itom in itoms}
        exp_status['i_f'] = ItomFaultStatusType.FAULTY
        ret_status = m.monitor(itoms)
        self.assertEqual(ret_status, exp_status, "wrong fault status")
        # only 2 relations (to view to judge which itom is faulty)
        itoms = {'i_a': 0, 'i_f': 3}
        exp_status = {itom: ItomFaultStatusType.UNDEFINED for itom in itoms}
        ret_status = m.monitor(itoms)
        self.assertEqual(ret_status, exp_status, "wrong fault status")
        # test another model (with utils)
        self.__model = SHSAModel(configfile="test/model_e2.yaml")
        m = SHSAMonitor(model=self.__model, domain='a')
        itoms = {'i_a': 4.03, 'i_b': 3.48, 'i_d': 2.0}
        exp_status = {itom: ItomFaultStatusType.OK for itom in itoms}
        ret_status = m.monitor(itoms)
        self.assertEqual(ret_status, exp_status, "wrong fault status")
        itoms = {'i_a': 4.5, 'i_b': 3.48, 'i_d': 2.0}
        exp_status = {itom: ItomFaultStatusType.OK for itom in itoms}
        exp_status['i_a'] = ItomFaultStatusType.FAULTY
        ret_status = m.monitor(itoms)
        self.assertEqual(ret_status, exp_status, "wrong fault status")
        # test models with constraints
        self.__model = SHSAModel(configfile="test/model_e3.yaml")
        m = SHSAMonitor(model=self.__model, domain='a')
        itoms = {'i_a': 4.5, 'i_b': 3.48, 'i_d': 4.0}
        exp_status = {itom: ItomFaultStatusType.UNDEFINED for itom in itoms}
        ret_status = m.monitor(itoms)
        self.assertEqual(ret_status, exp_status, "wrong fault status")
        self.__model = SHSAModel(configfile="test/model_e4.yaml")
        m = SHSAMonitor(model=self.__model, domain='a')
        itoms = {'i_a': 4.0, 'i_b': 3.48, 'i_d': 4.0}
        exp_status = {itom: ItomFaultStatusType.OK for itom in itoms}
        exp_status['i_d'] = ItomFaultStatusType.UNDEFINED
        ret_status = m.monitor(itoms)
        self.assertEqual(ret_status, exp_status, "wrong fault status")
        itoms = {'i_a': -4.0, 'i_b': -3.48, 'i_d': -4.0}
        exp_status = {itom: ItomFaultStatusType.UNDEFINED for itom in itoms}
        exp_status['i_a'] = ItomFaultStatusType.OK
        ret_status = m.monitor(itoms)
        self.assertEqual(ret_status, exp_status, "wrong fault status")

    def test_logfile(self):
        logfile = "monitor-log.yaml"
        # clean file
        with open(logfile, 'w') as f:
            pass
        model = SHSAModel(configfile="test/model_e1.yaml")
        m = SHSAMonitor(model, domain='a', logfile=logfile)
        self.assertEqual(m.logfile, logfile, "logfile not initialized")
        itoms = {'i_a': 0, 'i_f': 3}
        m.monitor(itoms)
        # one yaml dump expected
        # itoms, status and substitutions shall be part of the dump
        with open(logfile, 'r') as f:
            data = yaml.load(f)
            self.assertEqual(data['itoms']['i_a'], itoms['i_a'], "wrong log")
            self.assertEqual(data['status']['i_a'],
                             ItomFaultStatusType.UNDEFINED, "wrong log")
        # try more dumps
        itoms = {'i_a': 0, 'i_d': 0, 'i_e': 0, 'i_f': 0}
        m.monitor(itoms)
        itoms = {'i_a': 0, 'i_d': 0, 'i_e': 0, 'i_f': 1}
        m.monitor(itoms)
        cnt = 0
        with open(logfile, 'r') as f:
            for data in yaml.load_all(f):
                cnt = cnt + 1
        self.assertEqual(cnt, 3, "wrong number of yaml dumps")


if __name__ == '__main__':
        unittest.main()
