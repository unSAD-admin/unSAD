# Library Introduction

## Library Structure


data: store benchmark data for testing

src: store the source code


UCDT structure:

The source code is organized into 4 layers

utils <- common <- detectors <- test

layers at higher level have access to the functions defined in lower layers

utils: define basic utils functions that can be used by developers and users


common: define common logic that can be shared by multiple detectors, can only be used by developers


detectors: define core logic for anomaly detection


test: define test logic to test functions in other layers

