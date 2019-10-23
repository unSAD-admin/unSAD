# Created by Xinyu Zhu on 10/2/2019, 11:46 PM

# This files defines a set of annotation function which can be used in this project

import time
import threading


def profiling(func):
    """
    function with this decorator will print out the running time
    """

    def profiling_wrapper(*args, **kwargs):
        now = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - now
        print("Function", str(func), " took", duration, "seconds")
        return result

    return profiling_wrapper


def simple_thread(func):
    """
    function with this decorator will be run in a new thread
    A thread pool should be used if run in large scale
    """

    def simple_thread_wrapper(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.start()

    return simple_thread_wrapper
