import unittest

from engine.worker import Worker
from model.substitution import Substitution
from model.shsamodel import SHSAModel


class WorkerTestCase(unittest.TestCase):
    """Test cases for substitution workers."""

    def setUp(self):
        self.__model = SHSAModel(configfile="test/model1.yaml")
        self.__root = 'root'
        self.__nodes = ['t1']

    def tearDown(self):
        self.__subempty = None
        self.__subex = None

    def test_init(self):
        w = Worker(self.__nodes, model=self.__model, root=self.__root,
                   variables=['root'])
        self.assertEqual(len(w), len(self.__nodes),
                         "incorrect substitution length")
        self.assertTrue(w.has_next(), "variables to continue not initialized")
        w = Worker(self.__nodes, model=self.__model, root=self.__root,
                   relations=[('r2', 't5')])
        self.assertTrue(w.utility > 0, "utility not initialized")

    def test_one_next(self):
        w1 = Worker([], model=self.__model, root=self.__root,
                    variables=['root'])
        additional_w = w1.next()
        self.assertTrue(additional_w is not None and len(additional_w) > 0,
                        "no additional workers created")
        self.assertEqual(len(additional_w), 2,
                         "wrong number of additional workers created")
        u, r, rp = additional_w[0]
        w2 = Worker(r, root=self.__root, model=self.__model, utility=u,
                    relations=rp)
        u, r, rp = additional_w[1]
        w3 = Worker(r, root=self.__root, model=self.__model, utility=u,
                    relations=rp)
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
        w1 = Worker(model=model, root='a', variables=['a'])
        W = [w1]
        W.extend(w1.next())
        self.assertEqual(len(W), 1,
                         "additional workers created")
        self.assertTrue(w1.has_next(),
                        "no pending variables")
        W.extend(w1.next())
        self.assertEqual(len(W), 1,
                         "additional workers created")
        # correct number of worker
        model = SHSAModel(configfile="test/model_p4.yaml")
        w = Worker(model=model, root='root', variables=['root'])
        W = [w]
        W.extend(w.next())
        self.assertEqual(len(W), 2,
                         "number of workers mismatch")
        W.extend(w.next())
        self.assertEqual(len(W), 5,
                         "number of workers mismatch")


if __name__ == '__main__':
        unittest.main()
