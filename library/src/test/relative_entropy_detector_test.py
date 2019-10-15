# Created by Xinyu Zhu on 10/7/2019, 12:53 AM
import sys

from analysis import draw_array

sys.path.append("../")

from detectors.relative_entropy_detector import RelativeEntropyDetector


if __name__ == '__main__':
    detector = RelativeEntropyDetector()

    detector.initialize(input_min=1, input_max=100)

    all_result = []
    for i in range(1, 101):
        if i == 40:
            result = detector.handle_record({

                "value": 99
            })
            all_result.append(result)
            continue
        result = detector.handle_record({

            "value": i
        })
        all_result.append(result)

    print(all_result)

    draw_array(all_result)
