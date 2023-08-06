class PathNotFound(IOError):
    pass

class PathAlreadyExists(IOError):
     pass

class ConfigurableError(Exception):
    pass

class InvalidConfigParameter(ConfigurableError):
    pass

class ConfigDictError(ConfigurableError):
    pass