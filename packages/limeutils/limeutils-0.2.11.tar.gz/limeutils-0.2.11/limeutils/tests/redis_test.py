import pytest
from redis.exceptions import ResponseError
from limeutils import byte_conv, ValidationError       # noqa
from icecream import ic     # noqa



param = ['abc', 123, 12.5, 0, 'foo', 'foo', '']
@pytest.mark.parametrize('k', param)
# @pytest.mark.focus
def test_set(red, k):
    assert red.set('sam', k)
    assert red.get('sam') == k
    red.delete('sam')
    

# @pytest.mark.focus
def test_list(red):
    red.delete('many')
    red.set('many', ['a'])
    red.set('many', ['b'])
    red.set('many', ['c'], insert='start')
    red.set('many', ['d'], insert='start')
    assert red.llen(red.formatkey('many')) == 4
    assert (red.get('many')) == ['d', 'c', 'a', 'b']
    red.set('many', ['foo', 'bar'])
    assert red.llen(red.formatkey('many')) == 6
    assert (red.get('many')) == ['d', 'c', 'a', 'b', 'foo', 'bar']
    red.set('many', ['', 'meh'])
    assert red.llen(red.formatkey('many')) == 8
    assert (red.get('many')) == ['d', 'c', 'a', 'b', 'foo', 'bar', '', 'meh']
    red.delete('many')


# @pytest.mark.focus
def test_hash(red):
    red.delete('user')
    red.set('user', dict(age=34, username='enchance', gender='m'))
    assert red.get('user') == dict(age=34, username='enchance', gender='m')
    assert red.get('user', only='username') == dict(username='enchance')
    assert red.get('user', only=['age', 'gender']) == dict(age=34, gender='m')
    red.delete('user')


# @pytest.mark.focus
def test_get_none(red):
    red.delete('xxxyyyzzz')
    assert red.get('xxxyyyzzz') is None
    assert red.get('xxxyyyzzz', 'foo') == 'foo'
    assert red.get('xxxyyyzzz', []) == []
    assert red.get('xxxyyyzzz', [123, 345]) == [123, 345]
    assert red.get('xxxyyyzzz', [123, 345]) == [123, 345]
    assert red.get('xxxyyyzzz', {}) == {}
    assert red.get('xxxyyyzzz', dict(a='b')) == dict(a='b')
    assert red.get('xxxyyyzzz', 123) == 123
    assert red.get('xxxyyyzzz', True)
    assert not red.get('xxxyyyzzz', False)
    


# @pytest.mark.focus
def test_set_data(red):
    red.delete('norepeat')
    red.set('norepeat', {'b', 'a', 'c', 'd', 'a'})
    assert red.get('norepeat') == {'d', 'a', 'b', 'c'}   # unordered of course
    red.delete('norepeat')


param = [
    ('one', 432.5, ['one'], 1), ('two', ['b'], ['one', 'two'], 2),
    ('three', dict(age=34, username='sally', gender='f'), ['one', 'two', 'three'], 3)
]
@pytest.mark.parametrize('key, val, check, out', param)
# @pytest.mark.focus
def test_exists(red, key, val, check, out):
    red.set(key, val)
    assert red.exists(*check) == out
    assert isinstance(out, int)
    
    if check == ['one', 'two', 'three']:
        red.delete(*check)


# @pytest.mark.focus
def test_overwrite(nooverwrite):
    assert nooverwrite.set('a', 'a')
    
    with pytest.raises(ResponseError):
        nooverwrite.set('a', [1])
        assert nooverwrite.set('a', 1)
        assert nooverwrite.set('a', 12.5)
        assert nooverwrite.set('a', [12, 56])
        assert nooverwrite.set('a', dict(foo='bar'))
        
    nooverwrite.delete('a')
    

# @pytest.mark.focus
def test_exception(red):
    with pytest.raises(ValidationError):
        red.set('fail', ['a', 'b'], insert='foo')
        
    try:
        raise ValidationError(choices=['a', 'b'])
    except ValidationError as e:
        assert e.message == 'Arguments can only be: a or b.'
        # ic(e.message)

    try:
        raise ValidationError(choices=['a', 'b', 'c'])
    except ValidationError as e:
        assert e.message == 'Arguments can only be: a, b, or c.'
        # ic(e.message)

    try:
        raise ValidationError(choices=['a'])
    except ValidationError as e:
        assert e.message == 'Arguments can only be: a.'
        # ic(e.message)

    try:
        raise ValidationError('This is it.')
    except ValidationError as e:
        assert e.message == 'This is it.'
        # ic(e.message)
    red.delete('fail')


param = [
    ('ab', 'foo'), ('ab', 1), ('ab', [4, 5]), ('ab', dict(a=1, b=2)),
    (['hello', 'world'], ['foo', 'bar']), (['hello', 'world', 'x'], ['foo', 'bar', 123]),
]
@pytest.mark.parametrize('key, val', param)
# @pytest.mark.focus
# @pytest.mark.skip
def test_delete(red, key, val):
    if isinstance(key, str):
        red.set(key, val)
        v = red.get(key)
        assert v == val
        ret = red.delete(key)
        assert ret == 1
        v = red.get(key)
        assert v is None
        ret = red.delete(key)
        assert ret == 0
    else:
        for idx, k in enumerate(key):
            red.set(k, val[idx])
            assert red.get(k) == val[idx]
        ret = red.delete(*key)
        assert ret == len(key)
        for idx, k in enumerate(key):
            assert red.get(k) is None
