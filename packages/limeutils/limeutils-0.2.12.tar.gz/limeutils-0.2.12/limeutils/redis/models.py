from typing import Optional, Union, Any
from pydantic import BaseModel, Field, validator


VAL = Union[str, int, float, bytes]
LIST = Union[list, tuple]

#
#
# def listmaker(val):
#     """Validator: Convert str to list with one item."""
#     if isinstance(val, str):
#         return [val]
#     return val
#
# def nonone(val):
#     """Validator: Convert None to empty string."""
#     if val is None:
#         return ''
#     return val
#
# def nonone_mapping(val):
#     """Validator: Convert None to empty string."""
#     if val is None or not val:
#         return None
#     else:
#         for k, v in val.items():
#             val[k] = '' if v is None else v
#     return val


class StarterModel(BaseModel):
    """Shared fields"""
    key: VAL
    pre: Optional[VAL] = ''
    ver: Optional[VAL] = ''
    ttl: Optional[int] = Field(-1, ge=0)


# class Hset(StarterModel):
#     """Pydantic model for the hset() method"""
#     field: str
#     val: Optional[VAL]
#     mapping: Optional[dict] = None
#
#     _clean_val = validator('val', allow_reuse=True)(nonone)
#     _clean_mapping = validator('mapping', allow_reuse=True)(nonone_mapping)
#
#
# class Hmset(StarterModel):
#     """Pydantic model for the hmset() method"""
#     mapping: Optional[dict] = None
#
#     _clean_mapping = validator('mapping', allow_reuse=True)(nonone_mapping)
#
#
# class Set(StarterModel):
#     """Pydantic model for the set() method"""
#     val: Optional[VAL] = ''
#     xx: bool = False
#     keepttl: bool = False
#
#     _clean_val = validator('val', allow_reuse=True)(nonone)
#
#
#     @validator('xx', 'keepttl')
#     def boolonly(cls, val):
#         return bool(val)
#
#
# class Get(StarterModel):
#     """Pydantic model for the get() method"""
#     default: Optional[Any] = ''
#
#
# class Hget(StarterModel):
#     """Pydantic model for the get() method"""
#     default: Optional[Any] = ''
#
#
# class Hmget(StarterModel):
#     """Pydantic model for the hmget() method"""
#     fields_: Optional[LIST] = None
#
#
# class Hdel(StarterModel):
#     """Pydantic model for the hdel() method"""
#     fields_: Optional[Union[str, LIST]] = None
#
#     _clean_fields = validator('fields_', allow_reuse=True)(listmaker)
#
#
# class Delete(BaseModel):
#     """Pydantic model for the delete() method"""
#     key: Union[str, LIST]
#     pre: Optional[VAL] = ''
#     ver: Optional[VAL] = ''
#
#     _clean_fields = validator('key', allow_reuse=True)(listmaker)

