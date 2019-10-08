import numpy as np
# Normalize to 0-1
# Format:numpy array
# NOTE: only work for 1D data
class Normalizer:
    def __init__(self):
        pass
    def getNorm(self, x_train):
        self.max = np.max(x_train)
        self.min = np.min(x_train)
        self.gap = self.max - self.min
        return self.norm(x_train)
    def norm(self, data):
        return (data - self.min)/self.gap
    def denorm(self, data):
        return data * self.gap + self.min
