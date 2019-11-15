# Sequential-Anomaly-Detection-Library
Sequential Anomaly Detection Library





## Documentation

There are multiple anomaly detectors in this library, they use different algorithm and is designed to handle different
data format. 

LSTM Detector: for time series numerical data

HTM Detector: for time series numerical data

Relative Entropy Detector: for sequential numerical data

Context OSE Detector: for sequential numerical data

Symbolic Sequential Pattern Anomaly Detector: for sequential symbolic data

### HTM Detector

The HTM detector is designed to handle time series numerical data like this:

timestamp, value <br>
1234567, 12 <br>
1234568, 20 <br>
1234570, 30 <br>
....


The detector can accept either 2D array as input or array of dictionary as input<br>
If your data is an array of python dictionary like this:

    [
        {"time":123, "value":1}, 
        {"time":124, "value", 3}, 
        {"time":125, "value", 6},
        ...
    ]
    
Then you can set up the detector like this:

    from detectors.htm.htm_detector import HTMAnomalyDetector
    
    # prepare your data
    data =  [
        {"time":123, "value":1}, 
        {"time":124, "value", 3}, 
        {"time":125, "value", 6},
    ]
    
    
    # initialize the Detector by providing the name of keys in the dictionary
    detector = HTMAnomalyDetector("time", "value")
    
    # call the initialize method of the detector
    detector.initialize(docker_path="library/docker/htmDocker",
                        probation_number=int(len(data) * 0.15),
                        lower_data_limit=0,
                        upper_data_limit=10,
                        spatial_tolerance=0.05)
    
Here, as you can see there are 5 parameters required to initialize the detector, the docker_path specified the docker environment
used by the detector which is under library/docker/htmDocker. The initialize method actually provide 4 optional parameters related
to docker environment, you can choose to ask the detector to create or find an usable docker environment. 

Other parameters are data related: 

Remember, you don't have to provide these parameter when using the detector, there are default value. But providing these
parameter may help the detector do a better job.

probation_number: the number of sample used by the algorithm to learn normal pattern, an idea setting is the 0.15 * len(data), but
you may need to adjust this number to improve performance<br>
lower_data_limit: the minimum value that can be consider normal<br>
upper_data_limit: the maximum value that can be consider normal<br>
spatial_tolerance: how many percent of anomaly would you expect<br>

After initialization, you can start feeding data into the detector and get the outcome

There are two ways to do that:

    # Feeding a block of data
    
    result = detector.train(data)
    
    ---------------------------------
    result ->
    [
        {
            "anomalyScore": 0.6,
            "rawScore": 0.3
        },
        {
            "anomalyScore": 0.5,
            "rawScore": 0.2
        },
        {
            "anomalyScore": 0.3,
            "rawScore": 0.1
        }
     ]
     
     #######################################
     
     # Feeding streaming data
     
     for record in data:
        result = detector.handler_record(record)
        print(result)
    
    --------------------------------------
    {"anomalyScore": 0.6, "rawScore": 0.3}
    {"anomalyScore": 0.5, "rawScore": 0.2}
    {"anomalyScore": 0.3, "rawScore": 0.1}
    
    
You can also provide a 2D array:

    data =  [
        [123, 1], 
        [124, 3], 
        [125, 6],
        ...
    ]
    
    detector = HTMAnomalyDetector()
     
    detector.initialize(docker_path="library/docker/htmDocker",
                        probation_number=int(len(data) * 0.15),
                        lower_data_limit=0,
                        upper_data_limit=10,
                        spatial_tolerance=0.05)
                        
     result = detector.train(data)
     
    # or  
    # for record in data:
    #   result = detector.handler_record(record)
    #   print(result)
    
           
### ContextOSEDetector

ContextOSEDetector is designed for sequential numerical data, so it does not need the timestamp as an input which
simplified the input data format to 1D array

    data = [2,3,4,1,10]
    
    detector = ContextOSEDetector()
    
    # The hyper parameters have similar meaning as in HTM detector
    detector.initialize(min_value=min_value, max_value=max_value, probationary_period=150)
    
    
     for record in data:
        result = detector.handler_record(record)
        print(result) # This will give you the anomaly score between 1 and 0 with 0 being normal and 1 being abnormal
        
    # You can also provide the whole sequence as a block
    
    result = detector.handle_record_sequence(data)
    print(result) # This will price a list of anomaly score
    
One thing you need to notice is that we don't use train here to process a block of data because this detector, unlike
HTM detector does not need a training process, that is why they have slightly different API, you can also call 
handle_record_sequence on a HTM detector which is basically the same as train method


### RelativeEntropyDetector

The usage of RelativeEntropyDetector is almost the same as ContextOSEDetector except that it has different hyper parameters
 
    
    data = [2,3,4,1,10]
    
    detector = RelativeEntropyDetector()
    
    # The hyper parameters have similar meaning as in HTM detector
    detector.initialize(input_min=0, input_max=10, n_nins=5, window_size=52)
    
    
     for record in data:
        result = detector.handler_record(record)
        print(result) 
        
    # You can also provide the whole sequence as a block
    result = detector.handle_record_sequence(data)
    
    
    
### SequentialPatternAnomalyDetector
Symbolic Sequential Pattern Anomaly Detector is designed for sequential symbolic data like:

["A", "B", "A", "C", ...]

It treat every input element as a string symbol and return an anomaly score based on previous seem pattern:


    from detectors.symbolic.sequential_pattern import SequentialPatternAnomalyDetector

     
    data = ["A", "B", "A", "C", ...]
    
    detector = SequentialPatternAnomalyDetector()
    
    # initialize the detector with a window_size and a reduce_factor, for more information, please refer to the comment in source code
    detector.initialize(window_size=60, reduce_factor=2)
    
    
    result = detector.handle_record_sequence(data)
    
    # or you can provide a streaming of data:
    for record in data:
        result = detector.handle_record_sequence(record)
        print(result)
    
    
    




