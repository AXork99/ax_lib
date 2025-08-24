def flatten(args):
    from collections.abc import Iterable
    for arg in args:
        if isinstance(arg, Iterable) and not isinstance(arg, (str, bytes)): yield from flatten(arg)
        else: yield arg

def prologue(f):
    def wraps(g):
        def rez(*args, **kwargs):
            return g(f(*args, **kwargs))
        return rez
    return wraps

def epilogue(f):
    def wraps(g):
        def rez(*args, **kwargs):
            return f(g(*args, **kwargs))
        return rez
    return wraps

@prologue(flatten)
def avg(*args):
    return sum(args) / len(args)

@prologue(flatten)
def unordered(*x):
    return tuple(sorted(x))

def seeded(func):
    import numpy as np
    from functools import wraps
    from inspect import signature, Parameter
    
    sig = signature(func)
    params = list(sig.parameters.values())
    
    idx = next((i for i, p in enumerate(params) if p.kind == Parameter.VAR_KEYWORD), None)
    
    def insert_missing(kword):
        if kword not in sig.parameters:
            if idx is None:
                params.append(
                    Parameter(kword, Parameter.KEYWORD_ONLY, default=None)
                )
            else:
                params.insert(idx,
                    Parameter(kword, Parameter.KEYWORD_ONLY, default=None)
                )
    
    insert_missing('seed')
    insert_missing('rng')
    
    sig = sig.replace(parameters=params)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        from numpy.random import Generator, PCG64
        
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        
        seed = bound.arguments.get('seed')
        rng = bound.arguments.get('rng')
        
        if seed is None:
            seed = np.random.SeedSequence().entropy
            bound.arguments['seed'] = seed
            
        if rng is None:
            rng = Generator(PCG64(seed))
            bound.arguments['rng'] = rng
        
        if 'seed' not in func.__code__.co_varnames:
            bound.arguments.pop('seed', None)
            
        if 'rng' not in func.__code__.co_varnames:
            bound.arguments.pop('rng', None)
        
        return func(*bound.args, **bound.kwargs)
    
    wrapper.__signature__ = sig
    
    return wrapper    

# ---- SUS FIX LATER ----

def map_or_default(*obj, key, default=None):
    return (key(el) if el else (default[i] if isinstance(default, list) else default) for i, el in enumerate(obj))

def weight_avg(arr, weight : str = None, attr : str = None):
    from ..functional.math import IDENTITY, CONSTANT
    import numpy as np
    
    get_weight, get_attr = map_or_default(
        weight, attr, 
        key=lambda a: lambda x: getattr(x, a), 
        default=[CONSTANT(1), IDENTITY]
    )
    np.average(map(get_attr, arr), map(get_weight, arr))