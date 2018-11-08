from flask_caching import Cache
from werkzeug.local import LocalProxy


class CacheService(object):
    __version__ = 1

    _cache = None

    def __init__(self, app):
        self._cache = Cache(config={'CACHE_TYPE': 'simple'})
        self._cache.init_app(app)

    def set(self, key, value, prefix: str = '', timeout: int = None):
        self._cache.set(prefix + key, value, timeout=timeout)

    def add(self, key, value, prefix: str = ''):
        val = self.get(key=key, prefix=prefix)
        if val is not None:
            val.append(value)
        else:
            val = [value]
        self.set(key=key, value=val, prefix=prefix)

    def get(self, key, prefix: str = ''):
        value = self._cache.get(prefix + key)
        return value

    def delete(self, key, prefix: str = ''):
        self._cache.delete(prefix + key)
