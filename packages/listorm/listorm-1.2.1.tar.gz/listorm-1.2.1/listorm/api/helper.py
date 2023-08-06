from collections import abc

from ..utils import get_argcounts, filer_kwargs



def reduce_args_count(app, *args):
    if callable(app):
        args_count = get_argcounts(app)
        if args_count > 2:
            raise ValueError("{} can have no more than 2 args.".format(app))
        return app(*args[:args_count])
    return app


def reduce_where(item, where):
    if where is None:
        return True
    
    if not callable(where):
        raise ValueError('where must be callable')
    
    try:
        return where(**item)
    except TypeError:
        kwargs = filer_kwargs(item, where)
        return where(**kwargs)



def reduce_callback(item, key=None, app=None):
    updated = {}
    if not callable(app):
        if isinstance(app, abc.Mapping):
            value = app.get(item[key], item[key])
        else:
            value = app
    else:
        try:
            kwargs = filer_kwargs(item, app)
        except ValueError:
            value = app(item[key])
        else:
            try:
                value = app(**item)
            except TypeError:
                if kwargs:
                    value = app(**kwargs)
                else:
                    value = app(item[key])
    if key is None:
        return value

    updated[key] = value
    return updated
