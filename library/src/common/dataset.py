import numpy as np
from sklearn.model_selection import train_test_split
from io import StringIO
import unittest

class Dataset:
    def __init__(self):
        pass

    def getData(self):
        raise NotImplementedError

    def getDataBatch(self):
        raise NotImplementedError

# synthetic data
class SynthDataset(Dataset):
    def __init__(self):
        super().__init__()

    def getData(self):
        x_train = np.sin(np.linspace(-np.pi, np.pi, 201, dtype = np.float32))
        x_test = np.sin(np.linspace(-np.pi, np.pi, 201, dtype = np.float32))
        return x_train, x_test

# Get data from csv
class CSVDataset(Dataset):
    def __init__(self, filename, header=0, values=None, label=None, timestamp=None, test_size=0.1, batch_size=4096):
        super().__init__()
        self.filename = filename
        self.startrow = header
        self.header = header
        self.values = values
        self.label = label
        self.timestamp = timestamp
        self.test_size = test_size
        self.batch_size = batch_size

    def getData(self):
        if self.values is None:
            # All columns are values, no label or timestamp
            x = np.loadtxt(self.filename, skiprows=self.header, dtype=np.float32, delimiter=',')
            x_train, x_test = train_test_split(x, test_size=self.test_size, shuffle=False)
            return x_train, x_test
        else:
            # Get timestamp, values, label respectively
            data = np.loadtxt(self.filename, skiprows=self.header, dtype=str, delimiter=',')
            return self.splitData(data)


    def getDataBatch(self):
        if self.values is None:
            # All columns are values, no label or timestamp
            x = np.loadtxt(self.filename, skiprows=self.startrow, dtype=np.float32,
                           delimiter=',', max_rows=self.batch_size)
            self.startrow += x.shape[0]
            x_train, x_test = train_test_split(x, test_size=self.test_size, shuffle=False)
            return x_train, x_test
        else:
            # Get timestamp, values, label respectively
            data = np.loadtxt(self.filename, skiprows=self.header, dtype=str, delimiter=',',
                              max_rows=self.batch_size)
            self.startrow += data.shape[0]
            return self.splitData(data)

    def splitData(self, data):
        t, y = [], []
        if self.timestamp is not None:
            t = data[:, self.timestamp]
        x = data[:, self.values].astype(np.float32)
        if self.label is not None:
            y = data[:, self.label]
        t_train, t_test, x_train, x_test, y_train, y_test = train_test_split(
            t, x, y, test_size=self.test_size, shuffle=False)
        return {"timestamp": t_train, "values": x_train, "label": y_train}, \
               {"timestamp": t_test, "values": x_test, "label": y_test}

class TestCSV(unittest.TestCase):
    def test_simple(self):
        c = StringIO(u"1,2,3\n4,5,6\n7,8,9")
        dataset = CSVDataset(c, test_size=0.33)
        x_train, x_test = dataset.getData()
        self.assertEqual(x_train.dtype, np.float32)
        self.assertEqual(x_test.dtype, np.float32)
        arr_train = np.array([[1, 2, 3], [4, 5, 6]])
        arr_test = np.array([7, 8, 9])
        self.assertTrue(np.allclose(x_train, arr_train))
        self.assertTrue(np.allclose(x_test, arr_test))

    def test_full(self):
        c = StringIO(u"timestamp,x1,x2,label\n"
                     u"2019-10-01 00:00:00,1,0.05,Normal\n"
                     u"2019-10-01 00:01:00,2,0.97,Abnormal\n"
                     u"2019-10-01 00:02:00,3,0.03,Normal\n")
        dataset = CSVDataset(c, header=1, timestamp=0, values=(1,2), label=3, test_size=0.33)
        data_train, data_test = dataset.getData()
        tarr_train = np.array(["2019-10-01 00:00:00", "2019-10-01 00:01:00"])
        varr_train = np.array([[1, 0.05], [2, 0.97]])
        yarr_train = np.array(["Normal", "Abnormal"])
        self.assertTrue(np.alltrue(data_train["timestamp"] == tarr_train), msg=data_train["timestamp"])
        self.assertTrue(np.allclose(data_train["values"], varr_train), msg=data_train["values"])
        self.assertTrue(np.alltrue(data_train["label"] == yarr_train), msg=data_train["label"])

if __name__ == "__main__":
    unittest.main()