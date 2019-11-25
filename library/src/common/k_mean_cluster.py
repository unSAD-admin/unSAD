# Created by Xinyu Zhu on 11/22/2019, 3:28 PM

from sklearn.cluster import KMeans
import numpy as np


class KMeanTools:
    def __init__(self, arrays, k):
        self.kmeans = KMeans(n_clusters=k, random_state=0).fit(arrays)
        self.result = []
        for i in range(k):
            self.result.append([])
        for i, label in enumerate(self.kmeans.labels_):
            self.result[label].append(arrays[i])

    def predict_list(self, data):
        return self.kmeans.predict(data)

    def predict(self, data):
        return self.kmeans.predict(np.array([data]))[0]

    def get_clustered_data(self):
        return self.result


if __name__ == '__main__':
    X = np.array([[1, 2], [1, 4], [1, 0], [10, 2], [10, 4], [10, 0]])
    kmean = KMeanTools(X, 2)
    print(kmean.get_clustered_data())
    print(kmean.predict(np.array([[1, 2], [1, 2]])))
