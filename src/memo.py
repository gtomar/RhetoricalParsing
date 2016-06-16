import json, atexit, pickle
"""
Basic memoization library for persistent functions
memo_memoize_to_file accepts a filename for the cache
  and operates on functions which take a single hashable parameter

call memo_rebuild before decorating functions to force cache rebuilds

memo_iterable allows a single argument function to be called for each item in 
  a single iterable parameter (e.g. list of strings)

# Usage example:
##################################
@memo_iterable
@memo_memoize_to_file("myFunc.cache")
def myFunc(arg):
  ...

##################################

Created on May 10, 2015

@author: kmaki
"""

REBUILD_ALL_CACHES = False


def memo_pickle_first_to_file(fname):
  """
  Memoizes based on the first input
  """
  # Load persistent cache if not rebuilding                                    
  if not REBUILD_ALL_CACHES:                                                   
    try:
      cache = pickle.load(open(fname,'rb'))
    except (IOError, ValueError):
      cache = {}
  else:
    cache = {}
  
  # Set up persistence                                                         
  atexit.register(lambda: pickle.dump(cache, open(fname,'wb')))
  
  def memoized(func):
    def cachedfunc(inputs):
      if inputs[0] not in cache:
        cache[inputs[0]] = func(inputs)
      return cache[inputs[0]]
    return cachedfunc
  return memoized

def memo_pickle_to_file(fname):
  """                                                                          
  Memoization decorator maker for functions taking a single argument          
  Takes a filename to which the memoization may be cached to disk              
  If REBUILD_ALL_CACHES is True, does not load from caches                     
  """                                                                          
  # Load persistent cache if not rebuilding                                    
  if not REBUILD_ALL_CACHES:                                                   
    try:
      cache = pickle.load(open(fname,'rb'))
    except (IOError, ValueError):
      cache = {}
  else:
    cache = {}

  # Set up persistence                                                         
  atexit.register(lambda: pickle.dump(cache, open(fname,'wb')))
  # Memoize function outputs                                                   
  def memoized(func):
    def cachedfunc(inputs):
      if inputs not in cache:
        cache[inputs] = func(inputs)
      return cache[inputs]
    return cachedfunc
  return memoized

def memo_memoize_to_file(fname):                                               
  """                                                                          
  Memoization decorator maker for functions taking a single argument          
  Takes a filename to which the memoization may be cached to disk              
  If REBUILD_ALL_CACHES is True, does not load from caches                     
  """                                                                          
  # Load persistent cache if not rebuilding                                    
  if not REBUILD_ALL_CACHES:                                                   
    try:
      cache = json.load(open(fname,'r'))
    except (IOError, ValueError):
      cache = {}
  else:
    cache = {}

  # Set up persistence                                                         
  atexit.register(lambda: json.dumps(cache, open(fname,'w')))
  # Memoize function outputs                                                   
  def memoized(func):
    def cachedfunc(inputs):
      if inputs not in cache:
        cache[inputs] = func(inputs)
      return cache[inputs]
    return cachedfunc
  return memoized

def memo_iterable(func):
  def iterfunc(iterable):
    return [func(val) for val in iterable]
  return iterfunc
      
