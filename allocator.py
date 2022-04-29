# Simulate the fast path of the memory allocator, with/without Mallacc enabled.

## Parameters describing how many cycles each operation takes.
# TODO: figure out appropriate values

# Check the size of a memory request against the lower and upper bounds of a single range in the cache.
# This actually also includes the mapping from the requested size to size class index (Figure 5), which we don't explicitly model.
CHECK_AGAINST_RANGE = 5
# If cache hit, return the size class and allocation size corresponding to the requested size.
MCSZ_LOOKUP = 2
# mcszupdate takes as input the original requested size & corresponding size class + allocation size, and either updates 
# an existing cache entry, or inserts a new cache entry.
CACHE_UPDATE = 2 # update existing entry 
CACHE_INSERT = 2 # insert new entry
CACHE_EVICT = 2 # evict entry
# In the case of cache hit, need to pop Head, shift Next to Head, and prefetch the next Next.
# This encompasses mchdpop + mcnxtprefetch.
POP_HEAD_HIT = 3
# Upon deallocation, needs to push freed pointer to head of list; update cached Head + Next pointer (if exists in the cache)
MCHDPUSH = 3
# In the case of a cache miss, still need to perform the size class mapping, which takes a certain # of cycles in TCMalloc.
SZ_LOOKUP = 3
# In the case of a cache miss, still need to pop the head of the free list, which takes a certain # of cycles in TCMalloc.
POP_HEAD_MISS = 3


# TCMalloc size classes: The ith entry corresponds to size class i.
SIZE_CLASSES = [
	8,
	16,
	24,
	32,
	40,
	48,
	56,
	64
]

def malloc(sz, isMallaccEnabled, mallocCache):
	'''
	Takes as input the requested allocation size.

	Returns the number of cycles this call took.

	Because of how Queues are implemented, can't modify queue items in place. 
	Need to get() them, which removes them from the queue, modify them, then push back onto the queue. :((
	'''

	totalCycles = 0
	cache_hit = False
	cache = mallocCache.get()

	# Check <sz> against the lower and upper ranges of all entries in the malloc cache.
	cache_size = len(cache)
	for entry in cache:
		totalCycles += CHECK_AGAINST_RANGE
		lower = entry[0]
		upper = entry[1]
		if (sz >= lower) && (sz <= upper):
			cache_hit = True 
			break

	if cache_hit:
		# If cache hit, perform Mallacc logic
		totalCycles += MCSZ_LOOKUP
		totalCycles += POP_HEAD_HIT
	else:
		# If cache miss, fall back to normal code. 
		# TODO: Modify existing cache entry, or insert new one (and evict entry if necessary.)
		totalCycles += SZ_LOOKUP 
		totalCycles += POP_HEAD_MISS

	# Don't forget to push the modified cache back onto the queue! 
	mallocCache.put(cache)

	return totalCycles


def free(sz, isMallaccEnabled, mallocCache):
	'''
	Takes as input the size to be deallocated.

	Returns the number of cycles this call took.
	'''

	totalCycles = 0
	return totalCycles