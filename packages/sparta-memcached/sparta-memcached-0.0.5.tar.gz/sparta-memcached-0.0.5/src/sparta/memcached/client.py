import pylibmc


class KeyPrefixClient(pylibmc.Client):
    """
    Extends pylibmc.Client to support key_prefix.
    Also see https://github.com/memcached/memcached/wiki/Commands.
    """

    def __init__(
        self,
        servers,
        behaviors=None,
        binary=False,
        username=None,
        password=None,
        key_prefix=None,
    ):
        super().__init__(servers, behaviors, binary, username, password)
        self.key_prefix = key_prefix

    def _map_key(self, key):
        return self.key_prefix + key if self.key_prefix else key

    def add(self, key, *args, **kwargs):
        return super().add(self._map_key(key), *args, **kwargs)

    def add_multi(self, *args, **kwargs):
        raise NotImplementedError("multi operations not supported")

    def append(self, key, *args, **kwargs):
        return super().append(self._map_key(key), *args, **kwargs)

    def cas(self, key, *args, **kwargs):
        return super().cas(self._map_key(key), *args, **kwargs)

    def decr(self, key, *args, **kwargs):
        return super().decr(self._map_key(key), *args, **kwargs)

    def delete(self, key, *args, **kwargs):
        return super().delete(self._map_key(key), *args, **kwargs)

    def delete_multi(self, *args, **kwargs):
        raise NotImplementedError("multi operations not supported")

    def get(self, key, *args, **kwargs):
        return super().get(self._map_key(key), *args, **kwargs)

    def gets(self, key, *args, **kwargs):
        return super().gets(self._map_key(key), *args, **kwargs)

    def get_multi(self, *args, **kwargs):
        raise NotImplementedError("multi operations not supported")

    def incr(self, key, *args, **kwargs):
        return super().incr(self._map_key(key), *args, **kwargs)

    def incr_multi(self, *args, **kwargs):
        raise NotImplementedError("multi operations not supported")

    def prepend(self, key, *args, **kwargs):
        return super().prepend(self._map_key(key), *args, **kwargs)

    def replace(self, key, *args, **kwargs):
        return super().replace(self._map_key(key), *args, **kwargs)

    def set(self, key, *args, **kwargs):
        return super().set(self._map_key(key), *args, **kwargs)

    def set_multi(self, *args, **kwargs):
        raise NotImplementedError("multi operations not supported")

    def touch(self, key, *args, **kwargs):
        return super().touch(self._map_key(key), *args, **kwargs)
