import numpy as np
import unittest

# Base class to process data
class BaseDataProcessor:
    def __init__(self):
        pass

    # Traverse all training data and process them
    def process_training_data(self, data):
        raise NotImplementedError

    # Process testing data based on the parameters from training data
    def process_testing_data(self, data):
        raise NotImplementedError

    # Recover the data
    def recover_data(self, data):
        raise NotImplementedError

# Normalize: x' = (x - min(X)) / max(X) - min(X)
class Normalizer(BaseDataProcessor):
    def __init__(self, zero_mean = False):
        super().__init__()
        self.zero_mean = zero_mean

    def process_training_data(self, data):
        self.max = np.max(data, axis=0)
        self.min = np.min(data, axis=0)
        self.gap = self.max - self.min
        return self._norm(data)

    def process_testing_data(self, data):
        return self._norm(data)

    def recover_data(self, data):
        if self.zero_mean:
            data = (data + 1) / 2.
        return  data * self.gap + self.min

    def _norm(self, x):
        data = (x - self.min) / self.gap
        if self.zero_mean:
            data = data * 2. - 1
        return data

# Standardize: x' = (x - avg(X)) / std(X)
class Standardizer(BaseDataProcessor):
    def __init__(self, with_mean = True, with_std = True):
        super().__init__()
        self.with_mean = with_mean
        self.with_std = with_std

    def process_training_data(self, data):
        if self.with_mean:
            self.mean = np.mean(data, axis=0)
        else:
            self.mean = 0

        if self.with_std:
            self.std = np.std(data, axis=0)
        else:
            self.std = 1
        self._standardize(data)

    def process_testing_data(self, data):
        self._standardize(data)

    def recover_data(self, data):
        return data * self.std + self.mean

    def _standardize(self, x):
        return (x - self.mean) / self.std

# MaxAbsScale: x' = x / max(-min(X), max(X))
class MaxAbsScaler(BaseDataProcessor):
    def __init__(self):
        super().__init__()

    def process_training_data(self, data):
        amax = np.max(data, axis=0)
        amin = np.min(data, axis=0)
        self.max_abs = np.where(-amin > amax, amin, amax)
        return self._scale(data)

    def process_testing_data(self, data):
        return self._scale(data)

    def _scale(self, x):
        return x / self.max_abs


#TODO(Xingyang Liu) Add more data processors

class TestNormalizer(unittest.TestCase):
    def test_single(self):
        x = np.array([0., 1., 2., 3., 4., 5.])
        x_n = np.array([0., 0.2, 0.4, 0.6, 0.8, 1.])
        normalizer = Normalizer()
        res = normalizer.process_training_data(x)
        self.assertTrue(np.allclose(res, x_n), msg=res)

    def test_simple(self):
        x = np.array([[ 1., -1.,  2.],[ 2.,  0.,  0.],[ 0.,  1., -1.]])
        x_n = np.array([[ 0.5, 0,  1.],[ 1.,  0.5,  1.0/3],[ 0.,  1., 0]])
        normalizer = Normalizer()
        res = normalizer.process_training_data(x)
        self.assertTrue(np.allclose(res, x_n), msg=res)
        test = np.array([[ 1., -1.,  2.],[ 1., -1.,  2.],[ 1., -1.,  2.]])
        test_n = np.array([[ 0.5, 0,  1.],[ 0.5, 0,  1.],[ 0.5, 0,  1.]])
        res = normalizer.process_testing_data(test)
        self.assertTrue(np.allclose(res, test_n), msg=res)


if __name__ == "__main__":
    unittest.main()
