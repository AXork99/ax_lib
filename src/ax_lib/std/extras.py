def get_path_to_tmpdir(base: str = None):
    import os
    import sys
    
    script_path = base or sys.argv[0]
    
    abs_script_path = os.path.abspath(script_path)
    script_dir = os.path.dirname(abs_script_path)
    
    return os.path.join(script_dir, 'tmp')

PLACEHOLDER = get_path_to_tmpdir() + '/a'

def format_cmd(*args, **kwargs):
    cmd = []
    if args:
        cmd.extend(str(arg) for arg in args)
    
    if kwargs:
        for key, value in kwargs.items():
            if not key[0] == '-':
                if len(key) == 1:
                    prefix = "-"
                else:
                    prefix = "--"
            else: 
                prefix = ''
            
            if value is True:
                cmd.append(prefix + key)
            else:
                cmd.append(f"{prefix + key}={value}")
    return cmd

class Proxy:
    def __init__(self, val):
        self._val = val

    def get(p):
        return p._val

class Identifiable:
    ID = 0        
    def __init_subclass__(cls):
        cls.ID = 0
    
    def __init__(self):
        self.id = self.__class__.ID
        self.__class__.ID += 1

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Identifiable):
            return NotImplemented
        return self.id == other.id

def get_subclasses(cls: type):
    yield cls
    return (c for subcls in cls.__subclasses__() for c in get_subclasses(subcls))
