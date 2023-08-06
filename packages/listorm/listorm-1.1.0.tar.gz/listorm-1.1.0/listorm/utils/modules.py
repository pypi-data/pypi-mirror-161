import inspect



class Undefined(object):
    """ Undefined objects always and reliably "do nothing." """

    def __init__(self, default=None):
        self.default = default
    def __call__(self, *args, **kwargs): return self
    def __repr__(self): return "undefined"
    def __bool__(self): return False
    def __eq__(self, __o: object) -> bool:
        return self.default == __o.default
    def __hash__(self) -> int:
        return hash(self.default)



def get_argcounts(callable):
    try:
        sig = inspect.signature(callable)
    except:
        return 1
    else:
        return len(sig.parameters)

