import functools
import hashlib
from urllib.parse import quote

from django.core.cache import cache
from django.utils.encoding import force_bytes


def make_fragment_key(fragment_key: str, *vary_on):
    key = ":".join(quote(str(var)) for var in vary_on)
    args = hashlib.md5(force_bytes(key))
    return fragment_key % (args.hexdigest())


def cache_func(ttl):
    def decorator_cache(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = make_fragment_key(
                f"{func.__module__}.{func.__name__}.%s", args, kwargs
            )
            result = cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator_cache
