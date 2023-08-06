import pytest

import utils

@pytest.mark.parametrize('s, depth, expected', [
    ([[1,2,[3]],[],(4,5),6], 1, [1,2,[3],4,5,6]),
    ([[1,2,[3]],[],(4,5),6], -1, [1,2,3,4,5,6]),
    (tuple([[1,2,[3]],[],(4,5),6]), -1, (1,2,3,4,5,6)),
])
def test_flatten_seq(s, depth, expected):
    assert str(utils.itertools.flatten_seq(s, depth=depth)) == str(expected)
    
@pytest.mark.parametrize('d, depth, expected', [
    ({'a': {'b': {'c': 'd'}}}, 1, {'a.b': {'c': 'd'}}),
    ({'a': {'b': {'c': 'd'}}}, -1, {'a.b.c': 'd'}),
    ({'abc': {'bcd': {'cde': 'def'}}}, -1, {'abc.bcd.cde': 'def'}),
])
def test_flatten_dict(d, depth, expected):
    assert str(utils.itertools.flatten_dict(d, depth=depth)) == str(expected)
    
@pytest.mark.parametrize('d, depth, expected', [
    ({'a.b': {'b': {'c': 'd'}}}, 1, pytest.raises(ValueError)),
    ({'a.b': {'b': {'c': 'd'}}}, -1, pytest.raises(ValueError)),
])
def test_flatten_dict_exceptions(d, depth, expected):
    with expected:
        utils.itertools.flatten_dict(d, depth=depth)
    
@pytest.mark.parametrize('d, keys, value, expected', [
    ({}, ['a', 'b'], 'c', {'a': {'b': 'c'}}),
])
def test_assign_dict(d, keys, value, expected):
    utils.itertools.assign_dict(d, keys, value)
    assert str(d) == str(expected)
    
@pytest.mark.parametrize('enum', [
    False,
    True
])
def test_product(enum):
    l1 = [
        'hi',
        'bye',
    ]
    l2 = [
        3,
        7,
        9,
    ]
    expected_ndindices = [
        (0,0),
        (0,1),
        (0,2),
        (1,0),
        (1,1),
        (1,2),
    ]
    for i, elem in enumerate(utils.itertools.product(l1, l2, enum=enum)):
        if enum:
            ndidx, (e1, e2) = elem
            assert ndidx == expected_ndindices[i]
        else:
            e1, e2 = elem
        assert e1 == l1[expected_ndindices[i][0]]
        assert e2 == l2[expected_ndindices[i][1]]
        
@pytest.mark.parametrize('d1, d2, mode, fillvalue, expected', [
    ({'a': 1, 'b': 2}, {'b': 3, 'a': 4}, 'strict', None, {'a': (1,4), 'b': (2,3)}),
    ({'c': 5, 'a': 1, 'b': 2}, {'b': 3, 'a': 4, 'd': 6}, 'intersect', None, {'a': (1,4), 'b': (2,3)}),
    ({'c': 5, 'a': 1, 'b': 2}, {'d': 6, 'e': 7}, 'intersect', None, {}),
    ({'c': 5, 'a': 1, 'b': 2}, {'b': 3, 'a': 4, 'd': 6}, 'union', None, {'a': (1,4), 'b': (2,3), 'c': (5,None), 'd': (None,6)}),
    ({'c': 5, 'a': 1, 'b': 2}, {'b': 3, 'a': 4, 'd': 6}, 'union', 10, {'a': (1,4), 'b': (2,3), 'c': (5,10), 'd': (10,6)}),
])
def test_dict_zip(d1, d2, mode, fillvalue, expected):
    if mode != 'union':
        d = {k: (v1, v2) for k, v1, v2 in utils.itertools.dict_zip(d1, d2, mode=mode)}
    else:
        d = {k: (v1, v2) for k, v1, v2 in utils.itertools.dict_zip(d1, d2, mode=mode, fillvalue=fillvalue)}
    assert d == expected # no need for order of elemenets to be equal
    
@pytest.mark.parametrize('d1, d2, mode, expected', [
    ({'a': 1, 'b': 2, 'c': 3}, {'b': 3, 'a': 4}, 'strict', pytest.raises(ValueError)),
    ({'a': 1, 'c': 5}, {'b': 3, 'a': 4}, 'strict', pytest.raises(KeyError)),
    ({'a': 1, 'b': 2}, {'c': 5, 'b': 3, 'a': 4}, 'strict', pytest.raises(ValueError)),
    ({'a': 1, 'b': 2}, {'b': 3, 'a': 4}, 'whatever', pytest.raises(NotImplementedError)),
])
def test_dict_zip_exceptions(d1, d2, mode, expected):
    with expected:
        list(utils.itertools.dict_zip(d1, d2, mode=mode))
