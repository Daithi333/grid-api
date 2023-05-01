import functools
from collections import OrderedDict
from typing import List


class LRUCache:

    def __init__(self, maxsize: int):
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = self._generate_key(*args, **kwargs)
            cache = self.cache
            if key in cache:
                cache.move_to_end(key)
                self.hits += 1
                return cache[key]
            result = func(*args, **kwargs)
            cache[key] = result
            if len(cache) > self.maxsize:
                cache.popitem(last=False)
            self.misses += 1
            return result
        return wrapper

    def remove(self, *args, **kwargs) -> bool:
        key = self._generate_key(*args, **kwargs)
        if key in self.cache:
            self.cache.pop(key)
            return True
        return False

    def replace(self, value, *args, **kwargs):
        key = self._generate_key(*args, **kwargs)
        self.cache[key] = value

    def clear(self) -> bool:
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        return True

    def keys(self) -> List[str]:
        return list(self.cache.keys())

    def summary(self) -> dict:
        return {
            'currsize': len(self.cache),
            'maxsize': self.maxsize,
            'hits': self.hits,
            'misses': self.misses
        }

    def _generate_key(*args, **kwargs):
        id_ = kwargs.pop('id_')
        if not id_:
            raise Exception('id_ not found in kwargs')
        return id_
