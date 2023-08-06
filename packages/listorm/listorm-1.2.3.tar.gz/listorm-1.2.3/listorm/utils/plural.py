import functools

from collections import abc



def is_many_type(value) -> bool:
    if isinstance(value, abc.Iterable):
        if isinstance(value, abc.Mapping):
            return False
        elif isinstance(value, abc.Sequence):
            if isinstance(value, (str, bytes)):
                return False
        return True
    return False
    


def singulize(value) -> abc.Generator:
    if not is_many_type(value):
        if value is not None:
            yield value
    else:
        for row in value:
            yield from singulize(row)


def pluralize(value) -> list:
    pluralized = []
    if not is_many_type(value):
        if value is not None:
            pluralized.append(value)
    else:
        for row in value:
            pluralized += pluralize(row)
    return pluralized


def assingles(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        r = func(*args, **kwargs)
        yield from singulize(r)
    return wrapper