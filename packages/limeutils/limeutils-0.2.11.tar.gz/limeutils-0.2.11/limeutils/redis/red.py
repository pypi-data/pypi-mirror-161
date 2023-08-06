from redis import Redis
from typing import Optional, Union, Any, Literal
from pydantic import BaseModel
from redis.client import list_or_args
from redis.exceptions import ResponseError

from . import models
from icecream import ic
from .models import LIST, VAL, StarterModel
from limeutils import byte_conv, ValidationError, listify




class Red(Redis):
    
    def __init__(self, *args, **kwargs):
        self.pre = kwargs.pop('pre', '')
        self.ver = kwargs.pop('ver', '')
        self.ttl = kwargs.pop('ttl', -1)
        self.clear_wrongtype = kwargs.pop('wrongtype', True)
        super().__init__(*args, **kwargs)


    def stripper(self, key: str):
        """
        Removes the pre and ver from a key name
        :param key:     Key name
        :return:
        """
        pre = self.pre.strip()
        ver = self.ver.strip()

        ll = key.split(':')
        if pre and ver:
            if ll[0] == pre and ll[1] == ver:
                return ':'.join(ll[2:])
        elif pre and not ver:
            if ll[0] == pre:
                return ':'.join(ll[1:])
        elif not pre and ver:
            if ll[0] == ver:
                return ':'.join(ll[1:])
    
    
    def formatkey(self, key: str) -> str:
        """
        Create the final key name with prefix and/or version if necessary
        :param key: The key to format
        :return:    str
        """
        pre = self.pre.strip()
        ver = self.ver.strip()
        
        # Prevent multiple formatting which would be bad
        ll = key.split(':')
        if pre and ver:
            if ll[0] == pre and ll[1] == ver:
                return key
        elif pre and not ver:
            if ll[0] == pre:
                return key
        elif not pre and ver:
            if ll[0] == ver:
                return key

        ll = [pre, ver, key]
        ll = list(filter(None, ll))
        return ":".join(ll)


    def set(self, key: str, val: Union[VAL, LIST, set, dict], **kwargs):
        """
        Set and updates a key
        :param key:     Key name
        :param val:     Value to save. Could be any valid value inc dict or list
        :param kwargs:  Checks for clear, insert, and parent kwargs
        :return:        Depends on the type of key
        """
        key = self.formatkey(key)
        clear = kwargs.pop('clear', False)
        insert = kwargs.pop('insert', 'end')
        ex = kwargs.pop('ttl', self.ttl)
        
        if clear:
            self.delete(key)
        
        if isinstance(val, (str, int, float, bytes)):
            if self.clear_wrongtype and self._get_type(key) != 'string':
                self.delete(key)
            return super().set(key, val, ex=ex, **kwargs)
        
        elif isinstance(val, (list, tuple)):
            if self.clear_wrongtype and self._get_type(key) != 'list':
                self.delete(key)
                    
            if insert == 'end':
                ret = self.rpush(key, *val)
            elif insert == 'start':
                ret = self.lpush(key, *val)
            else:
                raise ValidationError(choices=['start', 'end'])
            
            if ex != -1:
                self.expire(key, ex)
            return ret
            
        elif isinstance(val, dict):
            if self.clear_wrongtype and self._get_type(key) != 'hash':
                self.delete(key)
            ret = self.hset(key, mapping=val)
            if ex != -1:
                self.expire(key, ex)
            return ret
        
        elif isinstance(val, set):
            if self.clear_wrongtype and self._get_type(key) != 'set':
                self.delete(key)
            ret = self.sadd(key, *val)
            if ex != -1:
                self.expire(key, ex)
            return ret
    
    
    def get(self, key: str, default=None, exact=True, **kwargs):
        """
        Get the value of a key
        :param key:     Key name
        :param default: Default value if key doesn't exist
        :param kwargs:  Checks for start, end, only, and parent kwargs
        :return:        Depends on the type of key
        """
        start = kwargs.pop('start', 0)
        end = kwargs.pop('end', -1)
        only = kwargs.pop('only', None)
        
        key = self.formatkey(key)
        datatype = byte_conv(super().type(key))
        
        if datatype == 'string':
            return byte_conv(super().get(key))
        
        elif datatype == 'list':
            data = super().lrange(key, start, end)
            return [byte_conv(i) for i in data]
        
        elif datatype == 'hash':
            if only:
                only = [only] if isinstance(only, str) else list(only)
                data = super().hmget(key, only)
                data = [byte_conv(i) for i in data]
                d = dict(zip(only, data))
            else:
                data = super().hgetall(key)
                d = {byte_conv(k):byte_conv(v) for k, v in data.items()}
            # ic(d)
            return d
        elif datatype == 'set':
            data = super().smembers(key)
            return {byte_conv(v) for v in data}
        return default


    def exists(self, *keys) -> int:
        """
        Checks if keys exists. Returns the number of keys that exist not which of the keys exists.
        :param keys:    Names of keys
        :return:        int No. of keys that exist
        """
        for i in keys:
            pass
        keys = [self.formatkey(i) for i in keys]
        return super().exists(*keys)
    
    
    def delete(self, *keys):
        """
        Delete keys
        :param keys:    Keys to delete
        :return:        int Number of keys deleted
        """
        keys = list(map(self.formatkey, keys))
        return super().delete(*keys)

    
    def _get_type(self, key: str):
        return byte_conv(super().type(key))


    def keys(self, pattern: str):
        """
        Get keys by pattern
        :param pattern: NOT regex. Just a simple string pattern. Ex. something-*
        :return:        list
        """
        fullkey = self.formatkey(pattern)
        key_list = [self.stripper(byte_conv(i)) for i in super().keys(fullkey)]
        return key_list


# class Redis:
#     def __init__(self, **kwargs):
#         self.conn = reds.Redis(**kwargs)
#
#
#
#
#
#     def hset(self, key: str, field: str, val: Optional[V] = '', mapping: Optional[dict] = None,
#              ttl=None, pre=None, ver=None) -> int:
#         data = models.Hset(key=key, field=field, val=val, mapping=mapping,
#                            ttl=ttl, pre=pre, ver=ver)
#         key = self.cleankey(data)
#         ttl = data.ttl if data.ttl is not None else self.ttl
#
#         self.pipe.hset(key, data.field, data.val, data.mapping)
#         self.pipe.expire(key, ttl)
#         [hset_ret, _] = self.pipe.execute()
#         return hset_ret