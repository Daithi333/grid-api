from abc import ABC, abstractmethod
from collections import OrderedDict
from functools import update_wrapper
from typing import List


class LRUCache(ABC):
    """
    Base Class for LRU Caching. Must be sub-classed and _generate_key implemented to specify what the cache keys should
    be, using the args and kwargs passed into the decorated function. Property 'maxsize' can be overridden in subclass.
    """
    def __init__(self, func, maxsize=128):
        self.cache = OrderedDict()
        self.func = func
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0
        update_wrapper(self, self.func)

    def __call__(self, *args, **kwargs):
        key = self._generate_key(*args, **kwargs)
        cache = self.cache
        if key in cache:
            cache.move_to_end(key)
            self.hits += 1
            return cache[key]
        result = self.func(*args, **kwargs)
        cache[key] = result
        if len(cache) > self.maxsize:
            cache.popitem(last=False)
        self.misses += 1
        return result

    def __repr__(self):
        return self.func.__repr__()

    def remove(self, *args) -> bool:
        key = self._generate_key(*args)
        if key in self.cache:
            self.cache.pop(key)
            return True
        return False

    def replace(self, value, *args):
        key = self._generate_key(*args)
        self.cache[key] = value

    def clear(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def keys(self) -> List[str]:
        return list(self.cache.keys())

    def summary(self) -> dict:
        return {
            'currsize': len(self.cache),
            'maxsize': self.maxsize,
            'hits': self.hits,
            'misses': self.misses
        }

    @abstractmethod
    def _generate_key(*args, **kwargs) -> str:
        raise NotImplementedError
