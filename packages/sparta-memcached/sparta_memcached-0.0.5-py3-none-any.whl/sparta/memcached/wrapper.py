import pylibmc


class KeyPrefixWrapper:
    """
    Wrapper around pylibmc.Client to support key_prefix.
    Also see https://github.com/memcached/memcached/wiki/Commands.
    """

    def __init__(
        self,
        client: pylibmc.Client,
        key_prefix,
    ):
        super().__init__()
        self.client = client
        self.key_prefix = key_prefix

    def _map_key(self, key):
        return self.key_prefix + key if self.key_prefix else key

    def __repr__(self):
        return "<%s for %s>" % (self.__class__.__name__, self.client)

    def __str__(self):
        return "<%s for %s>" % (self.__class__.__name__, self.client)

    def __getitem__(self, key):
        return self.client.__getitem__(self._map_key(key))

    def __setitem__(self, key, value):
        return self.client.__setitem__(self._map_key(key), value)

    def __delitem__(self, key):
        return self.client.__delitem__(self._map_key(key))

    def __contains__(self, key):
        return self.client.__contains__(self._map_key(key))

    def add(self, key, *args, **kwargs):
        return self.client.add(self._map_key(key), *args, **kwargs)

    def append(self, key, *args, **kwargs):
        return self.client.append(self._map_key(key), *args, **kwargs)

    def cas(self, key, *args, **kwargs):
        return self.client.cas(self._map_key(key), *args, **kwargs)

    def decr(self, key, *args, **kwargs):
        return self.client.decr(self._map_key(key), *args, **kwargs)

    def delete(self, key, *args, **kwargs):
        return self.client.delete(self._map_key(key), *args, **kwargs)

    def get(self, key, *args, **kwargs):
        return self.client.get(self._map_key(key), *args, **kwargs)

    def gets(self, key, *args, **kwargs):
        return self.client.gets(self._map_key(key), *args, **kwargs)

    def incr(self, key, *args, **kwargs):
        return self.client.incr(self._map_key(key), *args, **kwargs)

    def prepend(self, key, *args, **kwargs):
        return self.client.prepend(self._map_key(key), *args, **kwargs)

    def replace(self, key, *args, **kwargs):
        return self.client.replace(self._map_key(key), *args, **kwargs)

    def set(self, key, *args, **kwargs):
        return self.client.set(self._map_key(key), *args, **kwargs)

    def touch(self, key, *args, **kwargs):
        return self.client.touch(self._map_key(key), *args, **kwargs)
