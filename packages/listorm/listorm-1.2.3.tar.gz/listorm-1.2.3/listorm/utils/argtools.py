import inspect, functools



def get_param_type(func, param_name):
    sig = inspect.signature(func)
    for pname, param in sig.parameters.items():
        if pname == param_name:
            return param.kind
    raise TypeError('Cannot found {} in parameters of {}'.format(param_name, func))


def get_param_index(func, param_name):
    sig = inspect.signature(func)
    params = list(sig.parameters)
    try:
        index = params.index(param_name)
    except ValueError:
        raise ValueError("'{}' is not in parameters of {}".format(param_name, func))
    return index


def get_default(func, param_name):
    sig = inspect.signature(func)
    param = sig.parameters[param_name]
    return param.default


def update_params(func, param_name, callback, *args, **kwargs):
    args = list(args)
    kwargs = dict(kwargs)
    index = get_param_index(func, param_name)
    if index < len(args):
        args[index] = callback(args[index])
    else:
        if param_name in kwargs:
            kwargs[param_name] = callback(kwargs[param_name])
        else:
            kwargs[param_name] = get_default(func, param_name)

    return tuple(args), kwargs


def reduce_args(target):
    def wrapper(func):
        @functools.wraps(func)
        def reduce(*args, **kwargs):
            if target in kwargs:
                return func(*args, **kwargs)
            index = get_param_index(func, target)
            head, tail = args[:index], args[index:]
            reduced = []
            for arg in tail:
                if isinstance(arg, (list, tuple)):
                    reduced += arg
                else:
                    reduced.append(arg)
            return func(*head, reduced, **kwargs)
        return reduce
    return wrapper


def reduce_kwargs(target):
    def wrapper(func):
        @functools.wraps(func)
        def reduce(*args, **kwargs):
            if target in kwargs:
                return func(*args, **kwargs)            
            sig = inspect.signature(func)
            kw = {}
            rest = {}
            for key, value in kwargs.items():
                if key not in sig.parameters:
                    kw[key] = value
                else:
                    rest[key] = value
            kwargs = {
                target: kw
            }
            kwargs.update(rest)
            return func(*args, **kwargs)
        return reduce
    return wrapper
            

def _tuplizer(value):
    if value is None:
        return value
    if isinstance(value, (list, tuple)):
        return value
    return value,

def pluralize_params(*targets):
    targets = list(targets)
    def wrapper(func):
        @functools.wraps(func)
        def plural(*args, **kwargs):
            while targets:
                target = targets.pop()
                args, kwargs = update_params(
                    func, target,
                    _tuplizer,
                    *args, **kwargs
                )
            return func(*args, **kwargs)
        return plural
    return wrapper


def filer_kwargs(item, func):
    sig = inspect.signature(func)
    return {
        p: item[p] for p in sig.parameters if p in item
    }


def get_kwargnames(callable):
    sig = inspect.signature(callable)
    return list(sig.parameters)


def select_kwargs(callable, *args, allowed_params:list=None, **kwargs):
    allowed_params = allowed_params or []
    allowed_params += get_kwargnames(callable)
    kwargs = {
        key: value for key, value in kwargs.items()
        if key in allowed_params
    }
    return callable(*args, **kwargs)