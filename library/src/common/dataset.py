import numpy as np
from sklearn.model_selection import train_test_split
from io import StringIO
import unittest


class Dataset:  # Base class to get data
    def __init__(self):
        pass

    def get_data(self):
        raise NotImplementedError

    def get_data_batch(self):
        raise NotImplementedError


class SynthDataset(Dataset):  # Generate synthetic data, for test purpose
    def __init__(self):
        super().__init__()

    def get_data(self):
        x_train = np.sin(np.linspace(-np.pi, 3 * np.pi, 401, dtype=np.float32))
        x_test = np.sin(np.linspace(-np.pi, np.pi, 201, dtype=np.float32))
        y_train = np.zeros(401)
        y_test = np.zeros(201)
        return x_train, y_train, x_test, y_test


# Get data from csv
# filename: str, the path to csv file
# header: int, the number of header lines, these lines will be skipped, default is 0
# values: int or tuple, the indexes of columns which contain values
# timestamp: int or tuple, the indexes of columns which contain timestamp
# label: int or tuple, the indexes of columns which contain label
# test_size: float, the proportion of test set size among the whole dataset
# batch_size: float, the size of each batch
class CSVDataset(Dataset):
    def __init__(
            self,
            filename,
            header=0,
            values=None,
            label=None,
            timestamp=None,
            test_size=0.1,
            batch_size=4096,
            shuffle=False):
        super().__init__()
        self.filename = filename
        self.startrow = header
        self.header = header
        self.values = values
        self.label = label
        self.timestamp = timestamp
        self.test_size = test_size
        self.batch_size = batch_size
        self.shuffle = shuffle

    # Get all data from csv files
    # Return two sets of data, train and test
    # if no timestamp and labels: return two numpy array
    # else: return two dict {"timestamp": numpy array, "values": numpy array,
    # "label": numpy array}
    def get_data(self):
        if self.values is None:
            # All columns are values, no label or timestamp
            x = np.loadtxt(
                self.filename,
                skiprows=self.header,
                dtype=np.float32,
                delimiter=',')
            x_train, x_test = train_test_split(
                x, test_size=self.test_size, shuffle=self.shuffle)
            return x_train, x_test
        else:
            # Get timestamp, values, label respectively
            data = np.loadtxt(
                self.filename,
                skiprows=self.header,
                dtype=str,
                delimiter=',')
            return self._split_data(data)

    # Get data in batch from csv files
    # Return format are the same
    def get_data_batch(self):
        if self.values is None:
            # All columns are values, no label or timestamp
            x = np.loadtxt(
                self.filename,
                skiprows=self.startrow,
                dtype=np.float32,
                delimiter=',',
                max_rows=self.batch_size)
            self.startrow += x.shape[0]
            x_train, x_test = train_test_split(
                x, test_size=self.test_size, shuffle=self.shuffle)
            return x_train, x_test
        else:
            # Get timestamp, values, label respectively
            data = np.loadtxt(
                self.filename,
                skiprows=self.header,
                dtype=str,
                delimiter=',',
                max_rows=self.batch_size)
            self.startrow += data.shape[0]
            return self._split_data(data)

    # Split data to training data and testing data
    def _split_data(self, data):
        t_train, t_test, y_train, y_test = [], [], [], []
        if self.timestamp is not None:
            t = data[:, self.timestamp]
            t_train, t_test = train_test_split(
                t, test_size=self.test_size, shuffle=self.shuffle)
        x = data[:, self.values].astype(np.float32)
        x_train, x_test = train_test_split(
            x, test_size=self.test_size, shuffle=self.shuffle)
        if self.label is not None:
            y = data[:, self.label]
            y_train, y_test = train_test_split(
                y, test_size=self.test_size, shuffle=self.shuffle)
        return {"timestamp": t_train, "values": x_train, "label": y_train}, \
               {"timestamp": t_test, "values": x_test, "label": y_test}


class TestCSV(unittest.TestCase):
    def test_simple(self):
        c = StringIO(u"1,2,3\n4,5,6\n7,8,9")
        dataset = CSVDataset(c, test_size=0.33)
        x_train, x_test = dataset.get_data()
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
        dataset = CSVDataset(
            c, header=1, timestamp=0, values=(
                1, 2), label=3, test_size=0.33)
        data_train, data_test = dataset.get_data()
        tarr_train = np.array(["2019-10-01 00:00:00", "2019-10-01 00:01:00"])
        varr_train = np.array([[1, 0.05], [2, 0.97]])
        yarr_train = np.array(["Normal", "Abnormal"])
        self.assertTrue(
            np.alltrue(
                data_train["timestamp"] == tarr_train),
            msg=data_train["timestamp"])
        self.assertTrue(
            np.allclose(
                data_train["values"],
                varr_train),
            msg=data_train["values"])
        self.assertTrue(
            np.alltrue(
                data_train["label"] == yarr_train),
            msg=data_train["label"])


if __name__ == "__main__":
    unittest.main()
