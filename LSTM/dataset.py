import numpy as np
import torch
import unittest

class Dataset:
    def __init__(self):
        pass

# synthetic data
class SynthDataset(Dataset):
    def __init__(self):
        pass
    def getData(self):
        x_train = np.sin(np.linspace(-np.pi, np.pi, 201, dtype = np.float32))
        x_test = np.sin(np.linspace(-np.pi, np.pi, 201, dtype = np.float32))
        return x_train, x_test

class TestDataType(unittest.TestCase):
    def test_datatype(self):
        dataset = SynthDataset()
        x_train, x_test = dataset.getData()
        x_train_torch, x_test_torch = torch.from_numpy(x_train), torch.from_numpy(x_test)
        self.assertEqual(x_train_torch.dtype, torch.float32)
        self.assertEqual(x_test_torch.dtype, torch.float32)
        x_train_back, x_test_back = x_train_torch.numpy(), x_test_torch.numpy()
        self.assertTrue(np.array_equal(x_train_back, x_train))
        self.assertTrue(np.array_equal(x_test_back, x_test))

if __name__ == "__main__":
    unittest.main()
