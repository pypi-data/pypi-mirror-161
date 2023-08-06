from datetime import datetime, timezone, timedelta
from typing import Optional, Union, Tuple, Any
from ast import literal_eval
from enum import Enum, IntEnum
from icecream import ic



def istimezone(val: str) -> bool:
    """
    Check if the string is a valid timezone.
    :param val: String to check
    :return:    bool
    """
    # val = val.replace(':', '').strip()
    status = val in [
        '-1200', '-1100', '-1000', '-0930', '-0900', '-0800', '-0700', '-0600', '-0500', '-0400',
        '-0330', '-0300', '-0200', '-0100', '+0000', '+0100', '+0200', '+0300', '+0330', '+0400',
        '+0430', '+0500', '+0530', '+0545', '+0600', '+0630', '+0700', '+0800', '+0845', '+0900',
        '+0930', '+1000', '+1030', '+1100', '+1200', '+1245', '+1300', '+1400'
    ]
    return status


def isfloat(val: Union[int, float, str]):
    """
    Checks if the contents of a string is a float.
    :param val: String to parse
    :return:    bool
    """
    try:
        if isinstance(val, str):
            val.strip()
        float(val)
        return True
    except ValueError:
        return False
    

def byte_conv(val: Union[bytes, str]):
    """
    Converts bytes to a python string. This string could later be parsed into the correct
    python data type using parse_str(). Used mostly with Redis return values which always return in
    bytes.
    :param val: Bytes string to convert to python string
    :return:    str
    """
    if isinstance(val, str):
        return val
    
    try:
        x = val.decode()
        x = isinstance(x, bytes) and len(x) == 0 and '' or parse_str(x)
        return x
    except (UnicodeDecodeError, AttributeError):
        return val
    # return val.decode('utf-8')


def parse_str(string: str):
    """
    Converts a string to either an int, float, or str depending on its value.
    :param string:  String to convert
    :return:        int, float, or str
    """
    if not isinstance(string, str):
        raise ValueError('Only valid strings can be parsed.')
    
    string = string.strip()
    if istimezone(string):
        return string
    elif string.isdigit():
        return int(string)
    elif isfloat(string):
        return float(string)
    elif string in ['True', 'False']:
        return literal_eval(string)
    return string


def split_fullname(fullname: str, default: str = '',
                   prefix: Optional[Union[str, list, tuple]] = None,
                   suffix: Optional[Union[str, list, tuple]] = None) -> tuple:
    """
    Splits a fullname into their respective first_name and last_name fields.
    If only one name is given, that becomes the first_name
    :param fullname:    The name to split
    :param default:     The value if only one name is given
    :param prefix:      Custom prefixes to append to the default list
    :param suffix:      Custom suffixes to append to the default list
    :return:            tuple
    """
    if not fullname:
        return '', ''
    
    if prefix and not isinstance(prefix, (str, list, tuple)):
        raise TypeError('`prefix` must be a list/str for multi/single values.')

    if suffix and not isinstance(suffix, (str, list, tuple)):
        raise TypeError('`suffix` must be a list/str for multi/single values.')

    prefix = isinstance(prefix, str) and [prefix] or prefix or []
    suffix = isinstance(suffix, str) and [suffix] or suffix or []
    PREFIX_LASTNAME = ['dos', 'de', 'delos', 'san', 'dela', 'dona', *prefix]
    SUFFIX_LASTNAME = ['phd', 'md', 'rn', *suffix]

    list_ = fullname.split()
    lastname_idx = None
    if len(list_) > 2:
        for idx, val in enumerate(list_):
            if val.lower() in PREFIX_LASTNAME:
                lastname_idx = idx
                break
            elif val.lower().replace('.', '') in SUFFIX_LASTNAME:
                lastname_idx = idx - 1
            else:
                if idx == len(list_) - 1:
                    lastname_idx = idx
                else:
                    continue
        list_[:lastname_idx] = [' '.join(list_[:lastname_idx])]
        list_[1:] = [' '.join(list_[1:])]
    try:
        first, last = list_
    except ValueError:
        first, last = [*list_, default]
    return first, last


def oxford_comma(sequence: Union[list, tuple, set], separator: str = 'or'):
    sequence = sequence and list(sequence) or []
    if not sequence:
        return ''
    elif len(sequence) == 1:
        return sequence[0]
    elif len(sequence) == 2:
        return '{} {} {}'.format(', '.join(sequence[:-1]), separator, sequence[-1])
    elif len(sequence) >= 3:
        return '{}, {} {}'.format(', '.join(sequence[:-1]), separator, sequence[-1])
    
    
def listify(data: any) -> list:
    """
    A convenience function that converts data into a list unless it's already one.
    Bool is a subset of int.
    :param data:    Data to place into a list
    :return:        list
    """
    if isinstance(data, (list, set, tuple)):
        return list(data)
    return [data]


# TESTME: Untested
def valid_str_only(item, allow_bool: bool = False) -> bool:
    """
    Removes empty strings and other invalid values passed that aren't valid strings.
    :param item:        Check if valid str
    :param allow_bool:  Allow the use of bool only if True
    :return:            bool
    """
    if isinstance(item, str) and len(item) > 0:
        return True
    if allow_bool and item:
        return True
    return False


def setup_pagination(
    *, items: int = 10, total: int, page: int = 1, sort: str, direction: str = 'desc',
    asc: str = 'asc', dirflipper: str = '-', restartpage: bool = True, **_
) -> Tuple[str, int, int]:
    """
    Generate the values to be used in pagination
    :param items:           Number of rows to show
    :param total:           Total count for all rows
    :param page:            Page num
    :param sort:            Column to sort from
    :param direction:       asc or desc
    :param asc:             String to identify asc
    :param dirflipper:      String to identify a desc order
    :param restartpage:     If the page exceeds the maximimum, this shows page one instead
    :return:                tuple: orderby, offset, items
    """
    direction = '' if direction == asc else dirflipper
    orderby = f'{direction}{sort}'
    if restartpage and items * (page - 1) > total:
        page = 1
    offset = (page - 1) * items
    return orderby, offset, items


def offset_datetime(dt: datetime, offset: str) -> datetime:
    """
    Offsite the datetime instance to their local time
    :param dt:      Datetime to convert.
    :param offset:  Offset the dt by this amount. Accepts +08:00 or +8.
    :return:        Modified datetime according to offset
    """
    offset = offset.split(':')
    if len(offset) == 2:
        hours, mins = offset
        hours = int(hours.strip())
        mins = hours < 0 and int(mins.strip()) * -1 or int(mins.strip())
        mins += 60 * hours
    else:
        hours = int(offset[0].strip())
        mins = hours * 60
    
    tz = timezone(timedelta(minutes=mins))
    return dt.astimezone(tz)


# TESTME: Untested
def list_object_methods(obj: object):
    """
    List what methods are available for an objectn. Still untested.
    :param obj: Any class object (I think)
    :return:    Not sure yet
    """
    return [method_name for method_name in dir(obj) if callable(getattr(obj, method_name))]


def reverse_choices(choices: Union[Enum, IntEnum], value: Any):
    """
    For use with choices. Just pass the value and it will return the name associated to it.
    Good for reversing a db value (int) to its readable name attr
    :param choices: Enum, IntEnum
    :param value:   The value of the choice
    :return:        str
    """
    for i in choices:               # noqa
        if i.value == value:
            return i.name
        

def utc_to_offset(basedate: datetime, offset: str) -> datetime:
    """
    Shift a UTC datetime using an offset. Usefull for changing a user's date according
    to their saved timezone setting.
    :param basedate:    UTC datetime
    :param offset:      Offset to shift it to
    :return:            datetime
    """
    if not istimezone(offset):
        raise ValueError('The offset must be a valid GMT offset')
        
    newdate = basedate.replace(tzinfo=timezone.utc)
    newdate = newdate.astimezone(datetime.strptime(offset, '%z').tzinfo)
    return newdate