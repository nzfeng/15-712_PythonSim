# Simulate the fast path of the memory allocator, with/without Mallacc enabled.

from enum import Enum

class CacheEntry(Enum):
	SIZE_CLASS_IDX = 1
	TIME_COUNTER = 2

## ---- Parameters describing how many cycles each operation takes. TODO: need to decide appropriate values

# Check the size of a memory request against the lower and upper bounds of a single range in the cache.
# The malloc cache keys the array on the range of size class indices rather than the actual requested size range.
# So this actually also includes the mapping from the requested size to size class index (Figure 5).
# Should be fast since Mallacc has dedicated hardware to compute the index from the requested size.
# Specifically, the paper mentions: "The hard-coded hardware adds an additional cycle of latency to the cache."
CHECK_AGAINST_RANGE = 2
# If cache hit, return the size class and allocation size corresponding to the requested size.
MCSZ_LOOKUP = 1
# mcszupdate takes as input the original requested size & corresponding size class + allocation size, and either updates 
# an existing cache entry, or inserts a new cache entry.
CACHE_UPDATE = 1 # update existing entry 
CACHE_EVICT = 1 # evict entry
# In the case of cache hit, need to pop Head, shift Next to Head, and prefetch the next Next.
# This encompasses mchdpop + mcnxtprefetch.
POP_HEAD_HIT = 3
# Upon deallocation, needs to push freed pointer to head of list; update cached Head + Next pointer (if exists in the cache)
MCHDPUSH = 3
# In the case of a cache miss, still need to perform the size class mapping, which takes a certain # of cycles in TCMalloc.
SZ_LOOKUP = 20
# In the case of a cache miss, still need to pop the head of the free list, which takes a certain # of cycles in TCMalloc.
POP_HEAD_MISS = 20


def isCacheNotFull(cache):
	'''
	Given a malloc cache, determine whether the cache has empty entries. 
	If it does have an available entry, return the index of this entry in the cache.
	'''
	for (i, entry) in enumerate(cache):
		if entry[CacheEntry.SIZE_CLASS_IDX.value-1] == -1:
			return i 

	return None

def LRU(cache):
	'''
	Return the index of the least recently used cache entry.
	'''
	smallest_time = 0
	idx = 0
	for (i, entry) in enumerate(cache):
		if entry[CacheEntry.TIME_COUNTER.value-1] < smallest_time:
			smallest_time = entry[CacheEntry.TIME_COUNTER.value-1]
			idx = i 

	return idx 

def updateTimeCounters(cache, accessed):
	'''
	Decrement the counters of each entry except for the most recently used, which gets reset to 0.
	'''
	for i in range(len(cache)):
		if i != accessed:
			cache[i][CacheEntry.TIME_COUNTER.value-1] = 0
		else:
			cache[i][CacheEntry.TIME_COUNTER.value-1] -= 1


def sizeClassToIndex(sz):
	'''
	Size class mappings -- see gperftools/src/common.h
	'''
	big = sz > 1024
	add_amount = (127 + (120<<7)) if big else 7
	shift_amount = 7 if big else 3
	return (sz + add_amount) >> shift_amount

def updateCacheEntry(cache, index, sz):
	'''
	Update the entry at index <index> in the cache.
	'''
	szIdx = sizeClassToIndex(sz)
	# size_class_index = cache[index][CacheEntry.SIZE_CLASS_IDX-1]
	cache[index][CacheEntry.SIZE_CLASS_IDX.value-1] = szIdx
	cache[index][CacheEntry.TIME_COUNTER.value-1] = 0 

	
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

	if not isMallaccEnabled:
		totalCycles += SZ_LOOKUP
		totalCycles += POP_HEAD_MISS
		mallocCache.put(cache)
		return totalCycles 

	# Mallacc logic: Check <sz> against the lower and upper ranges of all entries in the malloc cache.
	# In practice, the range is essentially just one bracket though.
	cache_size = len(cache)
	szIdx = sizeClassToIndex(sz)
	for (i, entry) in enumerate(cache):
		totalCycles += CHECK_AGAINST_RANGE
		size_class_index = entry[CacheEntry.SIZE_CLASS_IDX.value-1]
		if (szIdx == size_class_index):
			cache_hit = True 
			updateTimeCounters(cache, i)
			break

	if cache_hit:
		# If cache hit, perform Mallacc logic
		totalCycles += MCSZ_LOOKUP
		totalCycles += POP_HEAD_HIT
	else:
		# If cache miss, fall back to normal code. 
		totalCycles += SZ_LOOKUP 
		totalCycles += POP_HEAD_MISS
		# Modify existing cache entry, or insert new one (and evict entry if necessary.)
		available = isCacheNotFull(cache)
		if available == None:
			idx = LRU(cache)
			updateCacheEntry(cache, idx, sz)
			totalCycles += CACHE_UPDATE
			totalCycles += CACHE_EVICT
		else:
			updateCacheEntry(cache, available, sz)
			totalCycles += CACHE_UPDATE

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