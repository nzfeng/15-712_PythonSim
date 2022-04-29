# Stripped-down Python simulator to better isolate multi-threaded Mallacc performance.

import argparse
import numpy as np
import os
import sys
import math
import time

# One MT benchmark where all threads are doing the same thing; 
# One benchmark where each thread is accessing a different size class at a given time 
# (perhaps just scramble the order of the strides); split the threads into 2 groups, 
# threads within each group is doing the same thing at the same time, but each group has different stride pattern. 

def st_speedup():
    '''
    '''
    pass

def main():
    '''
    Each "mode" represents a specific experiment to be run. Explanation of modes:

        st-speedup = Run all microbenchmarks with/without Mallacc instructions enabled (single-threaded.) 
                     Purpose is to validate that the basic modeling of memory allocation 
                     with/without Mallacc accurately approximates the output of XIOSim.

        mt-speedup = Run microbenchmarks, but with the given # of threads. 
        
        mt-cache-sweep = Same as mt-speedup, but sweep cache size from 2 - 32 entries.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("mode",
                        choices=["st-speedup",
                                 "mt-speedup",
                                 "mt-cache-sweep"])
    args = parser.parse_args()

if __name__ == "__main__":
    main()