import inspect



def tuplize(arg):
    if arg is None:
        return (arg)
    if isinstance(arg, (list, tuple)):
        return tuple(arg)
    return arg,


def str2float(value):
    try:
        ret = float(value)
    except:
        return value
    else:
        return ret

def round_try(value, round_to=2):
    try:
        if not isinstance(value, int):
            r = float(value)
        r = value
    except:
        return value
    else:
        return round(r, round_to)


def number_format(value, formats:object):
    if formats is None:
        return value
    formatter = type(formats)
    try:
        formatted = formatter(value)
    except Exception as e:
        asfloat = str2float(value)
        try:
            formatted = formatter(asfloat)
        except:
            formatted = formats
    return formatted


def get_argcounts(callable):
    try:
        sig = inspect.signature(callable)
    except:
        return 1
    else:
        return len(sig.parameters)
