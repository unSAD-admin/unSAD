# Created by Xinyu Zhu on 10/7/2019, 12:00 AM

import sys

from analysis import drawArray

sys.path.append("../")

from detectors.context_ose_detector import ContextOSEDetector

if __name__ == '__main__':
    detector = ContextOSEDetector()

    detector.initialize(min_value=1, max_value=100, probationary_period=5)
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

    drawArray(all_result)
