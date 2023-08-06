import json

import numpy as np
import tomli

def load(filename):
    filename = str(filename)
    if filename.endswith('.toml'):
        with open(filename, "rb") as f:
            config = tomli.load(f)
    elif filename.endswith('.json'):
        with open(filename, 'r') as f:
            config = json.load(f)
    else:
        raise NotImplementedError()
    
    return config

def dump(config, filename):
    filename = str(filename)
    if filename.endswith('.json'):
        with open(filename, 'w') as f:
            json.dump(config, f, indent=4)
    else:
        raise NotImplementedError()
        
def _replace_range_by_list(d, exclude=None):
    if exclude is None:
        exclude = []
    
    for k, v in d.items():
        if isinstance(v, dict) and k not in exclude:
            if any([vk not in ['start', 'stop', 'step'] for vk in v.keys()]):
                raise ValueError('configuration values cannot be dictionaries, unless it represents a range')
            d[k] = np.arange(**v).tolist()

def expand(d):
    _replace_range_by_list(d, exclude=['zip', 'prod'])
    
    configs = []
    
    e = {k: v for k, v in d.items() if k not in ['zip', 'prod']}
    if len(e) > 0:
        configs.append(e)
    
    if 'zip' in d:
        l = d['zip']
        if isinstance(l, dict):
            l = [l]
        assert isinstance(l, list)

        for e in l:
            assert isinstance(e, dict) and len(e) > 0
            _replace_range_by_list(e)

            Ns = [len(v) for v in e.values()]
            N = Ns[0]
            assert all([N == Ns[0] for N in Ns])

            configs += [{k: v[i] for k, v in e.items()} for i in range(N)]
    
    if 'prod' in d:
        l = d['prod']
        if isinstance(l, dict):
            l = [l]
        assert isinstance(l, list)

        for e in l:
            assert isinstance(e, dict)
            _replace_range_by_list(e)
            
            for k, v in e.items():
                if not isinstance(v, list):
                    e[k] = [v]

            ks, vs = zip(*list(e.items())) # gauranteed ks and vs are in same order
            shape = tuple([len(v) for v in vs])
            for indices in np.ndindex(shape):
                configs.append({k: v[i] for k, v, i in zip(ks, vs, indices)})
            
    return configs