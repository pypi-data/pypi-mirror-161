import random
import numpy as np
import torch

import utils

def test_set_seed():
    a0 = random.random()
    b0 = np.random.random()
    c0 = torch.rand(1)
    
    with utils.contextlib.set_seed(0):
        a1 = random.random()
        b1 = np.random.random()
        c1 = torch.rand(1)

    with utils.contextlib.set_seed(1):
        a2 = random.random()
        b2 = np.random.random()
        c2 = torch.rand(1)
        
    a3 = random.random()
    b3 = np.random.random()
    c3 = torch.rand(1)
    
    with utils.contextlib.set_seed(0):
        a4 = random.random()
        b4 = np.random.random()
        c4 = torch.rand(1)

    with utils.contextlib.set_seed(1):
        a5 = random.random()
        b5 = np.random.random()
        c5 = torch.rand(1)
        
    assert a1 == a4 and b1 == b4 and c1 == c4 # seed 0 vs seed 0
    assert a2 == a5 and b2 == b5 and c2 == c5 # seed 1 vs seed 1
    assert a1 != a2 and b1 != b2 and c1 != c2 # seed 0 vs seed 1
    assert a0 != a1 and b0 != b1 and c0 != c1 # random state vs seed 0
    assert a0 != a2 and b0 != b2 and c0 != c2 # random state vs seed 1
    assert a0 != a3 and b0 != b3 and c0 != c3 # random state vs random state