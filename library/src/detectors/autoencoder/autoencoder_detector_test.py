import os, sys
import numpy as np
import torch

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)

from detectors.autoencoder.autoencoder_detector import AutoEncoderDetector

if __name__ == '__main__':
    # unittest.main()
    detector = AutoEncoderDetector()
    detector.initialize(2)
    x_train = torch.tensor([[1.0, 2.0], [2.0, 3.0], [4.0, 5.0]])
    detector.train(x_train, num_epochs=3000, verbose=True)

    x_pred = detector.predict(x_train)
    print(x_pred)
    print(detector.predict(torch.tensor([[1.0, 2.0]])))
    print(detector.handle_record([1.0, 2.0]))

    # a = np.array([1,2,3])
    # b = np.array([4,5,6])
    # c = np.array([a,b])
    # print(c)
    # print(np.sum(c, axis=1))
