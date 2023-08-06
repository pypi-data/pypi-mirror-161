import pathlib

import pytest

import utils

@pytest.mark.parametrize('filename', [
    ('test_load_config.toml'),
    ('test_load_config.json'),
])
def test_load(filename, pytestconfig):
    data_path = pathlib.Path(pytestconfig.rootdir) / 'test' / 'data'
    config = utils.config.load(data_path / filename)
    assert config == {'a': 1, 'b': 'hi', 'c': True, 'd': [10, 11]}
    
def test_dump(tmp_path):
    config = {'a': 1, 'b': 'hi', 'c': True, 'd': [10, 11]}
    filename = tmp_path / 'config.json'
    utils.config.dump(config, filename)
    loaded_config = utils.config.load(filename)
    assert loaded_config == config
    
def test_expand(pytestconfig):
    filename = 'test_expand_config.toml'
    data_path = pathlib.Path(pytestconfig.rootdir) / 'test' / 'data'
    d = utils.config.load(data_path / filename)
    configs = utils.config.expand(d)
    print(*configs, sep='\n')
    assert configs == [
        {'a': 1, 'b': 'hihi', 'c': [0,1,2,3]},
        {'d': 2, 'e': 'hi'},
        {'d': 3, 'e': 'bye'},
        {'d': 4, 'e': 'beep'},
        {'d': 5, 'e': 'bop'},
        {'a': 1, 'b': 'hi', 'c': 'boop'},
        {'a': 1, 'b': 'bye', 'c': 'boop'},
        {'d': 2, 'e': 'hii'},
        {'d': 5, 'e': 'hii'},
        {'d': 8, 'e': 'hii'},
    ]
    
@pytest.mark.parametrize('filename', [
    ('test_expand_invalid_config_0.toml'),
    ('test_expand_invalid_config_1.toml'),
    ('test_expand_invalid_config_2.toml'),
])
def test_expand_invalid(filename, pytestconfig):
    data_path = pathlib.Path(pytestconfig.rootdir) / 'test' / 'data'
    d = utils.config.load(data_path / filename)
    with pytest.raises(ValueError):
        utils.config.expand(d)
        