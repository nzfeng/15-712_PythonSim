# Stripped-down Python simulator to better isolate multi-threaded Mallacc performance.

import argparse
import numpy as np
import os
import sys
import math
import time
import Queue
from threading import Thread
import benchmarks

# Stores the malloc cache, possibly multiple. Each item in the queue is a list representing a single cache; 
# each cache contains multiple 2-element lists, where the # of lists corresponds to the size of the cache (# of cache entries.)
# Each 2-element list is of the form [lower, upper], which represents the size range. 
# Size class info, size, head, next don't need to be explicitly simulated, since we don't actually have to allocate memory.
MALLOC_CACHE = Queue.Queue() 
# https://stackoverflow.com/a/19790994

def resetQueue(q):
    with q.mutex:
        q.queue.clear()

def st_speedup(nRuns):
    '''
    '''
    # print("Benchmarks: tp, tp_small, gauss")


    # Set up the malloc cache with the desired parameters.
    cache_size = 16 # default cache size is 16
    cache = [[-1,-1] for entry in range(cache_size)] # queue will have a single Mallacc for a single thread
    MALLOC_CACHE.put(cache) 

    # Baseline
    thread1 = Thread(target=benchmarks.tp, args=("Thread-1", False, MALLOC_CACHE))
    thread1.start()
    thread1.join()

    # resetQueue(MALLOC_CACHE)
    # MALLOC_CACHE.put(cache) 
    # thread1 = Thread(target=benchmarks.tp_small, args=("Thread-1", False, MALLOC_CACHE))
    # thread1.start()
    # thread1.join()

    # resetQueue(MALLOC_CACHE)
    # MALLOC_CACHE.put(cache) 
    # thread1 = Thread(target=benchmarks.gauss, args=("Thread-1", False, MALLOC_CACHE))
    # thread1.start()
    # thread1.join()

    # Mallacc-enabled
    resetQueue(MALLOC_CACHE)
    MALLOC_CACHE.put(cache) 
    thread1 = Thread(target=benchmarks.tp, args=("Thread-1", True, MALLOC_CACHE))
    thread1.start()
    thread1.join()

    # resetQueue(MALLOC_CACHE)
    # MALLOC_CACHE.put(cache) 
    # thread1 = Thread(target=benchmarks.tp_small, args=("Thread-1", True, MALLOC_CACHE))
    # thread1.start()
    # thread1.join()

    # resetQueue(MALLOC_CACHE)
    # MALLOC_CACHE.put(cache) 
    # thread1 = Thread(target=benchmarks.gauss, args=("Thread-1", True, MALLOC_CACHE))
    # thread1.start()
    # thread1.join()


def mt_speedup(nThreads, nRuns):
    '''
    Three MT benchmarks:

    One MT benchmark where each thread has the same workload.
    One MT benchmark where each thread has diverse workloads.
    One MT benchmark where the threads are split into 2 groups. 
    Within each group, each thread has the same workload, but each group has different workloads.
    This is meant to simulate a workload where there are multiple threads, but there is redundancy between threads' access patterns. 
    '''
    assert (num_threads % 2) == 0
    cache_size = 16
    cache = [[-1,-1] for entry in range(cache_size)] 
    MALLOC_CACHE.put(cache) # simulate a single cache for all threads

    pass

def mt_cache_sweep(nThreads, nRuns):
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
    parser = argparse.ArgumentParser(description='Run multi-threaded Mallacc experiments.')
    parser.add_argument('mode', help='Which experiment to run.',
                        choices=["st-speedup",
                                 "mt-speedup",
                                 "mt-cache-sweep"])
    parser.add_argument('--nRuns', default=1, help="Number of runs.")
    parser.add_argument('--nThreads', default=8, help='Number of threads, for the experiments that are multi-threaded.')
    args = parser.parse_args()

    if (args.mode == "st-speedup"):
        st_speedup(args.nRuns)
    elif (args.mode == "mt-speedup"):
        mt_speedup(args.nThreads, args.nRuns)
    elif (args.mode == "mt_cache_sweep"):
        mt_cache_sweep(args.nThreads, args.nRuns)

if __name__ == "__main__":
    main()