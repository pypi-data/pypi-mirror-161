import json
import copy

from utils import exceptions

class Parameter:
    def __init__(self, data=None, dtype=None, is_jsonable=True, deepcopy=False, load_callback=None):
        if dtype is not None:
            self.dtype = dtype
            
            if data is None:
                try:
                    data = dtype()
                except TypeError as err:
                    raise TypeError("dtype must be a python class that can be constructed without arguments")
        else:
            if data is None:
                raise ValueError("dtype must not be None when data is None")
                
            self.dtype = type(data)
            
        if is_jsonable:
            try:
                json.dumps(data)
            except (TypeError, OverflowError):
                raise exceptions.InvalidConfigParameter(f"data {data} is not json serializable," 
                                                        " try converting it to a compatible object type."
                                                        " If not possible, you can set is_jsonable=False,"
                                                        " but then you can't save the config dict as json.") from None
        self.deepcopy = deepcopy
        self.load_callback = load_callback
        self.set_data(data)
        
    def set_data(self, data):
        if self.deepcopy:
            data = copy.deepcopy(data)
        self._data = self.dtype(data)  # shallow copy
        
    def load(self, data):
        self.set_data(data)
        if self.load_callback is not None:
            self.load_callback(self)
        
    @property
    def data(self):
        data = self.dtype(self._data) # shallow copy
        if self.deepcopy:
            data = copy.deepcopy(data)
        return data
    
    def __repr__(self):
        return f"Parameter(data={self.data}, dtype={self.dtype}, deepcopy={self.deepcopy})"
        
class Configurable:
    # define __init__ with super() call to make this class suitable for multiple inheritance
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__parameters = {}
        self.__configurables = {}
        
    def __getattribute__(self, name):
        value = super().__getattribute__(name)
        if isinstance(value, Parameter):
            return value.data
        return value
    
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if isinstance(value, Parameter):
            if hasattr(self, '_Configurable__parameters'):
                self.__parameters[name] = value
            else:
                raise RuntimeError("Configurable must be initalized before setting Parameter")
        elif isinstance(value, Configurable):
            if hasattr(self, '_Configurable__configurables'):
                self.__configurables[name] = value
            else:
                raise RuntimeError("Configurable must be initalized before setting Configurable")
        else:
            if hasattr(self, '_Configurable__parameters') and name in self.__parameters:
                del self.__parameters[name]
            elif hasattr(self, '_Configurable__configurables') and name in self.__configurables:
                del self.__configurables[name]
    
    def __delattr__(self, name):
        if hasattr(self, '_Configurable__parameters') and name in self.__parameters:
            del self.__parameters[name]
        elif hasattr(self, '_Configurable__configurables') and name in self.__configurables:
            del self.__configurables[name]
        super().__delattr__(name)
    
    @property
    def params_dict(self):
        return self.__parameters
    
    @property
    def configurables_dict(self):
        return self.__configurables
    
    def config_dict(self):
        """
        Returns a configuration dictionary. Uses a flat instead of hierarchical structure
        because otherwise config parameters that are dictionaries will be ambiguous when trying
        to load them back in.
        """
        d = {}
        for name, param in self.params_dict.items():
            d[name] = param.data
        for name, configurable in self.configurables_dict.items():
            sub_d = configurable.config_dict()
            d.update({f'{name}.{sub_key}': sub_value for sub_key, sub_value in sub_d.items()})
        return d
    
    def _load_config_dict(self, config_dict, prefix, missing_keys, unexpected_keys):
        for name, param in self.params_dict.items():
            key = prefix + name
            try:
                value = config_dict[key]
                param.load(value)
            except KeyError as err:
                missing_keys.append(key)
                
            
        for key in config_dict.keys():
            if key.startswith(prefix):
                key_parts = key[len(prefix):].split('.')
                if len(key_parts) == 1 and key_parts[0] not in self.__parameters:
                    unexpected_keys.append(key)
    
    def load_config_dict(self, config_dict, strict=True):
        missing_keys = []
        unexpected_keys = []
        
        def load(configurable, prefix=''):
            configurable._load_config_dict(config_dict, prefix, missing_keys, unexpected_keys)
            for name, sub_configurable in configurable.configurables_dict.items():
                load(sub_configurable, prefix + name + '.')
        
        load(self)
        
        if strict:
            if not (len(missing_keys) == 0 and len(unexpected_keys) == 0):
                print(missing_keys)
                print(unexpected_keys)
                raise AssertionError("strict=True, but there is mismatch when loading config dict.")
        
# class Configurable:
#     # define __init__ with super() call to make this class suitable for multiple inheritance
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self._configs = {}
        
#     @property
#     def configs(self):
#         return self._configs
    
#     def __getattr__(self, name):
#         """
#         First checks whether name can be found using the super class's __getattr__
#         If not, then check whether name is in self._configs
#         """
#         try:
#             return super().__getattr__(name)
#         except AttributeError as err:
#             # Very important check! if self._configs doesn't exist, this will indefinitely recurse.
#             # This is because self._configs has already failed, so we shouldn't try to call self._configs again
#             # in the exception handling block.
#             # In general, for any name such self.name is called in this block (whether this is called explicitly
#             # or implicitly), we need to raise an error immediately whenever we encounter such name to prevent recursion.
#             if name == '_configs':
#                 raise
#             return self._configs[name]

#     def __setattr__(self, name, value):
#         if isinstance(value, Parameter):
#             if hasattr(self, name):
#                 delattr(self, name)
#             self.configs[name] = value.data
#         else:
#             if name in self.configs:
#                 del self.configs[name]
#             super().__setattr__(name, value)