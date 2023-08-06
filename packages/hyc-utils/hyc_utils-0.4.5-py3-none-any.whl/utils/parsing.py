import inspect
import argparse

def default_parser(func, configs=None, **kwargs):
    if configs is None:
        configs = {}

    signature = inspect.signature(func)
    
    parser = argparse.ArgumentParser(**kwargs)
    for k, v in signature.parameters.items():
        if k in configs and 'opt_str' in configs[k]:
            option_strings_k = configs[k]['opt_str']
        else:
            if v.default is inspect.Parameter.empty:
                option_strings_k = []
            else:
                if len(k) == 1:
                    option_strings_k = [f'-{k}'.replace('_','-')]
                else:
                    option_strings_k = [f'--{k}'.replace('_','-')]
                
        if k in configs and 'type' in configs[k]:
            type_k = configs[k]['type']
        else:
            if v.annotation is inspect.Parameter.empty:
                type_k = str
            else:
                type_k = v.annotation
                interpretable_types = [str, int, float, bool]
                if not any(type_k == t for t in interpretable_types):
                    raise ValueError(f"type {type_k} for argument {k} is not recognized. Please provide the type manually")
                
        if k in configs and 'nargs' in configs[k]:
            nargs_k = configs[k]['nargs']
        else:
            nargs_k = None
            
        if k in configs and 'default' in configs[k]:
            default_k = configs[k]['default']
        else:
            if v.default is inspect.Parameter.empty:
                default_k = None
            else:
                default_k = v.default
                
        if k in configs and 'help' in configs[k]:
            help_k = configs[k]['help']
        else:
            help_k = k.replace('_', ' ')
            
        if k in configs and 'action' in configs[k]:
            action_k = configs[k]['action']
            if action_k in ['store_true', 'store_false']:
                parser.add_argument(*option_strings_k, dest=k, action=action_k, help=help_k)
            else:
                raise NotImplementedError()
        else:
            help_k = f'{help_k} (dtype: {type_k.__name__})'

            if v.default is not inspect.Parameter.empty:
                help_k = f'{help_k} (default: {default_k})'
            else:
                help_k = f'{help_k} (required argument)'
                
            if v.default is inspect.Parameter.empty and len(option_strings_k) > 0:
                parser.add_argument(*option_strings_k, dest=k, type=type_k, nargs=nargs_k, default=default_k, help=help_k, required=True)
            else:
                parser.add_argument(*option_strings_k, dest=k, type=type_k, nargs=nargs_k, default=default_k, help=help_k)
        
    return parser

def multi_parse(parsers, **kwargs):
    parser = argparse.ArgumentParser(parents=parsers)
    _ = parser.parse_args(**kwargs) # we don't use the output of the combined parser, only needed for checking validity of input and providing an aggregated help message
    out = []
    for parser in parsers:
        args, _ = parser.parse_known_args(**kwargs)
        out.append(args)
    return out