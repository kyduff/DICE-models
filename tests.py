#!/usr/bin/env python

import timeit
import numpy as np
from specs import ModelSpec
import simulator


def time_test():
    N = 100
    test_input = np.array([0.5] + [0.5]*100 + [0.5]*100)
    mspec = ModelSpec()
    
    return timeit.Timer(lambda: simulator.objective(test_input, mspec)).autorange()

if __name__ == '__main__':
    nloops, ttl_time = time_test()
    print(f"time per loop: {1e3*ttl_time/nloops} ms")