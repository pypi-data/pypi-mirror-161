import torch

import utils
import utils.configurable as conf

class SubModule(conf.Configurable, torch.nn.Module):
    def __init__(self, a):
        super().__init__()
        self.W = torch.nn.Parameter(torch.ones(2,2))
        self.x = conf.Parameter(dtype=int)
        self.a = a
        
class Module(conf.Configurable, torch.nn.Module):
    def __init__(self, y, z):
        super().__init__()
        self.sub_module = SubModule(conf.Parameter([0,1,2.1]))
        self.y = y
        self.z = z

def test_dict_save_load(tmp_path):
    tmp_path_1 = tmp_path / 'config.json'
    tmp_path_2 = tmp_path / 'state_dict.pth.tar'
    
    m1 = Module(conf.Parameter([1,2]), torch.nn.Parameter(torch.zeros(2,2)))
    utils.io.save_config(tmp_path_1, m1.config_dict())
    torch.save(m1.state_dict(), tmp_path_2)
    
    m2 = Module(conf.Parameter([3,4]), torch.nn.Parameter(10*torch.ones(2,2)))
    config_dict = utils.io.load_config(tmp_path_1)
    state_dict = torch.load(tmp_path_2)
    m2.load_config_dict(config_dict)
    m2.load_state_dict(state_dict)
    
    assert m1.y == m2.y == [1,2]
    assert torch.allclose(m1.z, m2.z)
    assert m1.sub_module.x == m2.sub_module.x == 0
    assert m1.sub_module.a == m2.sub_module.a == [0,1,2.1]
    assert torch.allclose(m1.sub_module.W, m2.sub_module.W)
    
def test_conflicting_attributes():
    m1 = Module(conf.Parameter([1,2]), torch.nn.Parameter(torch.zeros(2,2)))
    m1.y = (10,)
    assert 'y' not in m1.config_dict() and m1.y == (10,)
    m1.y = conf.Parameter(dtype=tuple)
    assert m1.y == tuple()
    m1.y = None
    assert 'y' not in m1.config_dict() and m1.y is None
    m1.sub_module = None
    assert list(m1.config_dict().items()) == []
    m1.y = conf.Parameter(10)
    assert list(m1.config_dict().items()) == [('y',10)]