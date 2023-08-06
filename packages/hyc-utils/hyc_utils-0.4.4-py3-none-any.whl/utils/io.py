import pathlib
import os
import pickle
import json

import utils

def save(path, data, extension=None, depth=-1, overwrite=False):
    """
    Saves data at path.
    If path has a suffix and extension is provided, then 
    the suffix must match the extension, and the data 
    is stored as a single file with the specified extension at path.
    If path has a suffix and no extension is provided, then
    the extension is inferred and the data is also stored
    as a single file.
    The depth parameter is ignored in both these case.
    If path does not have suffix, then path is the directory in which
    the data is stored. The data must be a dictionary.
    The depth parameter controls the depth of the directory.
    If depth=0, then path will become a depth 0 directory, and
    if depth=-1, then path will be a directory as deep as the data dictionary.
    """
    path = pathlib.Path(path)
    
    if extension is None:
        extension = path.suffix[1:]
    
    if extension == 'pkl':
        def save_func(filename, dat):
            with open(filename, 'wb') as f:
                pickle.dump(dat, f)
    elif extension == 'json':
        def save_func(filename, dat):
            with open(filename, 'w') as f:
                json.dump(dat, f, indent=4)
    else:
        raise NotImplementedError(f"Extension {extension} is not yet implemented")
    
    if path.suffix != '': # path is a filename
        suffix = path.suffix[1:]
        if suffix != extension:
            raise ValueError(f"path suffix must match extension if suffix is present. suffix: {suffix}, extension: {extension}.")
        if not overwrite and path.is_file():
            raise utils.exceptions.PathAlreadyExists(f"The file {str(path)} already exists.")
        path.parent.mkdir(parents=True, exist_ok=True)
        save_func(path, data)
        
    else: # path is a directory
        for key, val in utils.itertools.flatten_dict(data, depth=depth).items():
            filename = path / f"{'/'.join(key.split('.'))}.{extension}"
            filename.parent.mkdir(parents=True, exist_ok=True)
            if not overwrite and filename.is_file():
                raise utils.exceptions.PathAlreadyExists(f"The file {str(filename)} already exists.")
            save_func(filename, val)
        
def save_data(path, data_dict, **kwargs):
    save(path, data_dict, 'pkl', **kwargs)
    
def save_config(path, config, **kwargs):
    save(path, config, 'json', **kwargs)
    
def load(path, extension=None):
    path = pathlib.Path(path)
    if not path.exists():
        raise utils.exceptions.PathNotFound(f"The path {path} does not exist.")
        
    if extension is None:
        extension = path.suffix[1:]
        
    if extension == 'pkl':
        def load_func(filename):
            with open(filename, 'rb') as f:
                return pickle.load(f)
    elif extension == 'json':
        def load_func(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    else:
        raise NotImplementedError(f"Extension {extension} is not yet implemented")
        
    if path.is_file():
        data = load_func(path)
    elif path.is_dir():
        data = {}
        for cur_path, dirnames, filenames in os.walk(path):
            if '.ipynb_checkpoints' not in cur_path:
                for filename in filenames:
                    filename = pathlib.Path(filename)
                    if filename.suffix == f'.{extension}':
                        cur_path_rel = pathlib.Path(cur_path).relative_to(path)
                        utils.itertools.assign_dict(data, [*cur_path_rel.parts,filename.stem], load_func(os.path.join(cur_path,filename)))
    else:
        raise IOError(f"Path {path} is neither file nor directory")
        
    return data
        
def load_data(path):
    return load(path, 'pkl')

def load_config(path):
    return load(path, 'json')