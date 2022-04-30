# The microbenchmarks.

import random
import numpy as np
from allocator import *

# These parameters are copied from gperftools/num_iterations.h
ITERATIONS = 32768 
# ITERATIONS = 1
REPEATS = 13

# Parameters for each benchmark:
#		
#	mallocCache = a Queue object representing the malloc cache (possibly multiple)
#	isMallaccEnabled = whether Mallacc optimizations are enabled
#	

def tp(threadName, isMallaccEnabled=False, mallocCache = None, nIterations=ITERATIONS):

	'''
	A series of back-to-back fast-path malloc and free calls. 
	Sizes are requested in increments of 16 bytes, from 32 to 512 bytes.

	Return the # of cycles per malloc call & free call, averaged over all iterations/runs.
	'''
	
	totalMallocCycles = 0
	totalFreeCycles = 0
	nMallocCalls = 0
	nFreeCalls = 0

	sz = 32
	for i in range(nIterations):
		totalMallocCycles += malloc(sz, isMallaccEnabled, mallocCache)
		nMallocCalls += 1
		totalFreeCycles += free(sz, isMallaccEnabled, mallocCache)
		nFreeCalls += 1
		sz += 16
		if (sz > 512): sz = 32

	print "%s\t tp\t mallacc=%s: %f %f" %(threadName, isMallaccEnabled, totalMallocCycles/nMallocCalls, totalFreeCycles/nFreeCalls)


def tp_small(threadName, isMallaccEnabled=False, mallocCache = None, nIterations=ITERATIONS):

	totalMallocCycles = 0
	totalFreeCycles = 0
	nMallocCalls = 0
	nFreeCalls = 0

	sz = 8
	for i in range(nIterations):
		totalMallocCycles += malloc(sz, isMallaccEnabled, mallocCache)
		nMallocCalls += 1
		totalFreeCycles += free(sz, isMallaccEnabled, mallocCache)
		nFreeCalls += 1
		sz += 32
		if (sz > 128): sz = 8

	print "%s\t tp_small:\t mallacc=%s: %f %f" %(threadName, isMallaccEnabled, totalMallocCycles/nMallocCalls, totalFreeCycles/nFreeCalls)


def gauss(threadName, isMallaccEnabled=False, mallocCache = None, nIterations=ITERATIONS):
	
	totalMallocCycles = 0
	nMallocCalls = 0

	for i in range(nIterations):
		# 90% of sizes are drawn from the smaller set
		whichSet = random.random()
		# Actual implementation in gperftools uses piecewise_constant_distributions
		sz = int(random.uniform(16, 64))
		if whichSet > 0.9: int(random.uniform(256, 512))

		totalMallocCycles += malloc(sz, isMallaccEnabled, mallocCache)
		nMallocCalls += 1

	print "%s\t gauss:\t mallacc=%s: %f" %(threadName, isMallaccEnabled, totalMallocCycles/nMallocCalls)


def gauss_free(nIterations=ITERATIONS):
	pass

def sized_deletes(nIterations=ITERATIONS):
	pass

# no antagonist() because this one requires modeling CPU caches