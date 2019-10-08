import numpy as np
import unittest

class BaseDataProcessor:
    def __init__(self):
        pass

    def processTrainingData(self, data):
        raise NotImplementedError

    def processTestingData(self, data):
        raise NotImplementedError

    def recoverData(self, data):
        raise NotImplementedError

class Normalizer(BaseDataProcessor):
    def __init__(self):
        super().__init__()

    def processTrainingData(self, data):
        self.max = np.max(data, axis=0)
        self.min = np.min(data, axis=0)
        self.gap = self.max - self.min
        return self._norm(data)

    def processTestingData(self, data):
        return self._norm(data)

    def recoverData(self, data):
        return data * self.gap + self.min

    def _norm(self, x):
        return (x - self.min) / self.gap

#TODO(Xingyang Liu) Add more data processors

class TestNormalizer(unittest.TestCase):
    def test_simple(self):
        x = np.array([[ 1., -1.,  2.],[ 2.,  0.,  0.],[ 0.,  1., -1.]])
        x_n = np.array([[ 0.5, 0,  1.],[ 1.,  0.5,  1.0/3],[ 0.,  1., 0]])
        normalizer = Normalizer()
        res = normalizer.processTrainingData(x)
        self.assertTrue(np.allclose(res, x_n), msg=res)
        test = np.array([[ 1., -1.,  2.],[ 1., -1.,  2.],[ 1., -1.,  2.]])
        test_n = np.array([[ 0.5, 0,  1.],[ 0.5, 0,  1.],[ 0.5, 0,  1.]])
        res = normalizer.processTestingData(test)
        self.assertTrue(np.allclose(res, test_n), msg=res)


if __name__ == "__main__":
    unittest.main()