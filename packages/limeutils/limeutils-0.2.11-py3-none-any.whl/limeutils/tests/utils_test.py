import pytest, pytz
from datetime import datetime
from collections import Counter

import pytz
from icecream import ic
from limeutils import utils, listify, valid_str_only, istimezone, utc_to_offset


param = [(3, True), (3.0, True), (0, True), ('3.4', True), ('0.4', True), ('0.0', True),
         ('0', True), ('3.0', True), ('3', True), ('abc', False), ('3,344', False),
         ('3,344.5', False), ('3,344.00', False)]
@pytest.mark.parametrize('val, out', param)
def test_isfloat(val, out):
    assert utils.isfloat(val) is out


param = [('123', 123), ('12.3', 12.3), ('a1b2c3', 'a1b2c3'), ('abc', 'abc'), ('', ''), ('-', '-'),
         (None, ValueError), (bytes(), ValueError), ('True', True), ('False', False),]
@pytest.mark.parametrize('val, out', param)
def test_parse_str(val, out):
    try:
        assert utils.parse_str(val) == out
    except out:
        with pytest.raises(out):
            assert utils.parse_str(val)


param = [('Hey You', ('Hey', 'You')), ('Sir Hey You', ('Sir Hey', 'You')),
         ('Sir Hey You Phd', ('Sir Hey', 'You Phd')), ('Hey delos You', ('Hey', 'delos You')),
         ('Hey san You', ('Hey', 'san You')),
         ('Eliza Maria Erica dona Aurora Phd Md', ('Eliza Maria Erica', 'dona Aurora Phd Md'))]
@pytest.mark.parametrize('val, out', param)
def test_split_fullname(val, out):
    assert utils.split_fullname(val) == out


param = [('abra', 'fed'), ('abra', 6.22), ('abra', 789), ('abra', '1.5'), ('abra', '123')]
@pytest.mark.parametrize('key, val', param)
def test_byte_conv(red, key, val):
    red.set(key, val)
    if val == '123':
        val = 123
    if val == '1.5':
        val = 1.5
    assert red.get(key) == val


param = [
    (['one', 'two', 'three', 'four'], 'one, two, three, or four'),
    (['one', 'two', 'three'], 'one, two, or three'),
    (['one', 'two'], 'one or two'),
    (['one'], 'one'), ([], '')
]
@pytest.mark.parametrize('seq, out', param)
@pytest.mark.utilfocus
def test_oxford_comma(seq, out):
    assert utils.oxford_comma(seq) == out


param = [
    ('foo', ['foo']), (['foo'], ['foo']),
    (1, [1]), (12.5, [12.5]),
    (['foo', 'bar'], ['foo', 'bar']),
    (('foo',), ['foo']), (('foo', 'bar'), ['foo', 'bar']),
    ({'foo'}, ['foo']), ({'foo', 'bar'}, ['foo', 'bar']),
    (True, [True]), (False, [False])
]
@pytest.mark.parametrize('data, out', param)
# @pytest.mark.focus
def test_listify(data, out):
    assert Counter(listify(data)) == Counter(out)


param = [
    ('', False, False), ([], False, False), (None, False, False), (1, False, False),
    (1.5, False, False), (False, False, False), (True, False, False), ('a', False, True),
    (set(), False, False), ('', False, False), (True, True, True), (False, True, False)
]
@pytest.mark.parametrize('item, allow, out', param)
# @pytest.mark.focus
def test_valid_str_only(item, allow, out):
    if allow:
        assert valid_str_only(item, allow_bool=True) == out
    else:
        assert valid_str_only(item) == out


param = [
    ('-1200', True), ('-0800', True), ('-0330', True), ('-0100', True),
    ('+0800', True), ('+0000', True), ('+1300', True), ('+0100', True),
    ('0800', False), ('0000', False), ('1300', False),
    ('+1500', False), ('-1300', False)
]
@pytest.mark.parametrize('tz, out', param)
# @pytest.mark.focus
def test_istimezone(tz, out):
    assert istimezone(tz) == out


param = [
    (datetime(2020, 1, 1, 10, 30, 1, tzinfo=pytz.UTC), '+0000', '2020-01-01 10:30:01 +0000'),
    (datetime(2020, 1, 1, 10, 30, 1, tzinfo=pytz.UTC), '+0100', '2020-01-01 11:30:01 +0100'),
    (datetime(2020, 1, 1, 10, 30, 1, tzinfo=pytz.UTC), '+0500', '2020-01-01 15:30:01 +0500'),
    (datetime(2020, 1, 1, 10, 30, 1, tzinfo=pytz.UTC), '+1200', '2020-01-01 22:30:01 +1200'),
    (datetime(2020, 1, 1, 10, 30, 1, tzinfo=pytz.UTC), '-0330', '2020-01-01 07:00:01 -0330'),
    (datetime(2020, 1, 1, 20, 30, 1, tzinfo=pytz.UTC), '+0900', '2020-01-02 05:30:01 +0900'),
    (datetime(2020, 1, 1, 20, 30, 1, tzinfo=pytz.UTC), '-0200', '2020-01-01 18:30:01 -0200'),
    (datetime(2020, 1, 1, 20, 30, 1, tzinfo=pytz.UTC), '-1200', '2020-01-01 08:30:01 -1200'),
    (datetime(2020, 1, 1, 3, 30, 1, tzinfo=pytz.UTC), '-0700', '2019-12-31 20:30:01 -0700'),
]
@pytest.mark.parametrize('basedate, offset, datestr', param)
# @pytest.mark.focus
def test_utc_to_offset(basedate, offset, datestr):
    date_format = '%Y-%m-%d %H:%M:%S %z'

    newdate = utc_to_offset(basedate, offset)
    assert isinstance(newdate, datetime)
    assert newdate.strftime('%z') == offset
    assert newdate.strftime(date_format) == datestr