import unittest

from engine.worker import Worker
from model.substitution import Substitution
from model.shsamodel import SHSAModel


class WorkerTestCase(unittest.TestCase):
    """Test cases for substitution workers."""

    def setUp(self):
        model = SHSAModel(configfile="test/model1.yaml")
        self.__subempty = Substitution(model=model, root='root')
        nodes = ['t1']
        self.__subex = Substitution(model=model, root='root')
        self.__subex.extend(nodes)

    def tearDown(self):
        self.__subempty = None
        self.__subex = None

    def test_init(self):
        w = Worker(self.__subempty, variables=['root'])
        self.assertTrue(w.has_next(), "variables to continue not initialized")
        w = Worker(self.__subex, relations=[('r2', 't5')])
        self.assertTrue(w.utility > 0, "utility not initialized")

    def test_one_next(self):
        w1 = Worker(self.__subempty, ['root'])
        additional_w = w1.next()
        self.assertTrue(additional_w is not None and len(additional_w) > 0,
                        "no additional workers created")
        self.assertEqual(len(additional_w), 2,
                         "wrong number of additional workers created")
        w2 = additional_w[0]
        w3 = additional_w[1]
        done = 0
        if not w1.has_next():
            done += 1
        if not w2.has_next():
            done += 1
        if not w3.has_next():
            done += 1
        self.assertEqual(done, 3,
                         "wrong number of finished workers")

    def test_next(self):
        model = SHSAModel(configfile="test/model_p1.yaml")
        sub = Substitution(model=model, root='a')
        w1 = Worker(sub, variables=['a'])
        W = [w1]
        W.extend(w1.next())
        self.assertEqual(len(W), 1,
                         "additional workers created")
        self.assertTrue(w1.has_next(),
                        "no pending variables")
        W.extend(w1.next())
        self.assertEqual(len(W), 1,
                         "additional workers created")


if __name__ == '__main__':
        unittest.main()
