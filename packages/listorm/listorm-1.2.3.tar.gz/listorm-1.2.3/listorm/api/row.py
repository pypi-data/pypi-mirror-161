"""
Functional API for dict as row
------------------------------------

"""

from typing import List, Dict, Tuple, Callable, Text, Any

from .helper import reduce_args_count, reduce_callback
from ..utils import number_format, reduce_args, reduce_kwargs



def askeys(item:Dict, excludes:List=None):
    """extract keys from item

    :param item: a dict object
    :param excludes: keys for excluded, defaults to None
    :return: a list contains keys of item


    .. doctest::  

        >>> import listorm

        >>> item = {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'}

        >>> listorm.askeys(item)
        ['name', 'gender', 'age', 'location']

        >>> listorm.askeys(item, excludes=['gender', 'age'])
        ['name', 'location']

    """

    excludes = excludes or []
    return [
        key for key in item if key not in excludes
    ]



@reduce_args('keys')
def asvalues(item:Dict, keys:List, *, exact:bool=False, flat:bool=True):    
    """extract values from item that matchs the order of keys

    :param item: a dict object
    :param keys: keys for retrive values
    :param exact: if True, raise KeyError when key is not in item, defaults to False
    :param flat: When the return value is a single value, the value is returned without being included in the tuple, defaults to True
    :return: a tuple of contains values or a value


    .. doctest::

        >>> item = {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'}

        >>> listorm.asvalues(item, ['name', 'gender']) #  listify keys
        ('Smith', 'M')

        >>> listorm.asvalues(item, 'name', 'gender') # also as unpacked args
        ('Smith', 'M')

        >>> listorm.asvalues(item, 'name') # unpacked when retriving single value
        'Smith'

        >>> listorm.asvalues(item, 'name', flat=False) # if flat=False, the sigle value is also packed as a tuple.
        ('Smith',)

    """

    keys = keys or askeys(item)
    result = tuple(
        item[key] for key in keys if exact or key in item
    )
    if flat and len(result) == 1:
        return result[0]
    return result


@reduce_args('keys')
def asselect(item:Dict, keys:List, *, excludes:List=None) -> Dict:
    """select key, value pair from item

    :param item: a dict object
    :param keys: the arguments for keys or a list containing keys, if nothing, returns a new dict with the same key and value as the original item.
    :param excludes: keys for excluded, defaults to None
    :return: new dict item as selected


    .. doctest::

        >>> item = {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'}

        >>> listorm.asselect(item, ['name', 'gender']) # keys arg as list
        {'name': 'Smith', 'gender': 'M'}

        >>> listorm.asselect(item, 'name', 'gender') # equal from above that keys as unpacked args
        {'name': 'Smith', 'gender': 'M'}

        >>> listorm.asselect(item) # pass a nothing of keys arg
        {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'}

        >>> listorm.asselect(item, excludes=['gender']) # useful when need to drop item
        {'name': 'Smith', 'age': 17, 'location': 'USA'}

    """
    keys = keys or askeys(item)
    keys = [
        key for key in keys
        if key not in (excludes or [])
    ]
    return {
        key:item[key] for key in keys if key in item
    }


@reduce_kwargs('keymap')
def addkeys(item:Dict, *, keymap:Dict) -> Dict:
    """extends item keys values via value or callback

    :param item: a dict object
    :param keymap: key: value pair dict of items to be added
    :return: Expanded existing items


    .. doctest::

        >>> item = {'name': 'Smith', 'gender': 'M', 'age': 17}

        >>> listorm.addkeys(item, keymap={'location': 'USA'})
        {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'}

        >>> listorm.addkeys(item, location='USA') # also keymap can converted into kwargs style
        {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'}
        
        # add key value via function
        >>> listorm.addkeys(item,
        ...    gender_age=lambda gender, age: "{}/{}".format(gender, age)
        ... )
        {'name': 'Smith', 'gender': 'M', 'age': 17, 'gender_age': 'M/17'}


    .. note::
    
        * The lambda callback function used in this library is applied according to the number and name of the argument 
        * Refers to the keys in the item by specifying it as the lambda arguments


        .. code-block:: python

            lambda gender, age: "{}/{}".format(gender, age) # gender and age are key name of item
        * For refer to all items in a lambda, you can use **kwargs pattern, for example, when reffering space character exists in item

        .. code-block:: python

            lambda **kwargs: kwargs['age of ultron'] == 19  # (ex: when space exists in key name)

    """
    
    added = {}
    for key, app in keymap.items():
        added.update(reduce_callback(item, key, app))

    item = dict(item)
    item.update(added)
    return item


@reduce_kwargs('renamemap')
def asrename(item:Dict, *, renamemap:Dict) -> Dict:
    """change key as to another name

    :param item: a dict object
    :param renamemap: old: new name pair of dict
    :return: newly renamed dict


    .. doctest::

        >>> import listorm

        >>> item = {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'}

        >>> listorm.asrename(item, renamemap={'name': 'first_name', 'gender': 'sex', 'location': 'country'})
        {'first_name': 'Smith', 'sex': 'M', 'age': 17, 'country': 'USA'}

        >>> listorm.asrename(item, name='first_name', gender='sex', location='country') # also as uppacked kwarg style
        {'first_name': 'Smith', 'sex': 'M', 'age': 17, 'country': 'USA'}

    """
    return {
        renamemap.get(key, key): value
        for key, value in item.items()
    }


@reduce_kwargs('defaultmap')
def asdefault(item:Dict, *, defaultmap:Dict) -> Dict:
    """fill values from defaults if key not in existing item

    :param item: a dict object
    :param defaultmap: defaults key:value mapping for missing items
    :return: newly normalized dict


    .. doctest::
    
        >>> normal_item = {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'}

        >>> # nothing is happend when applied at normal_item which has not missing values at location
        >>> listorm.asdefault(normal_item, location='Unknown')
        {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'}

        >>> # item that has missing keys for location and age
        >>> missing_location_and_age = {'name': 'Smith', 'gender': 'M'}

        >>> # filled with defaults values at missing keys
        >>> listorm.asdefault(missing_location_and_age, location='Earth', age=10)
        {'name': 'Smith', 'gender': 'M', 'location': 'Earth', 'age': 10}

        >>> # fill value by function
        >>> missing_location = {'name': 'Smith', 'gender': 'M', 'age': 17}

        >>> def fill_location(age): # argument name age matched with age as key in item
        ...     return 'Universe' if age > 100 else 'Earth'

        >>> # Changing the location by referring to the neighboring key age
        >>> listorm.asdefault(missing_location, location=fill_location)
        {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'Earth'}

    """

    defaults = asselect(defaultmap, excludes=askeys(item))
    return addkeys(item, keymap=defaults)


def asdiff(item1:Dict, item2:Dict) -> List:
    """Finds keys with different value from common keys of two items

    :param item1: a dict object
    :param item2: anothor dict object
    :return: list of keys 


    .. doctest::

        >>> item1 = {'name': 'Xiaomi', 'product': 'battery', 'amount':7}
        >>> item2 = {'name': 'Park', 'product': 'battery', 'amount':2}
        >>> listorm.asdiff(item1, item2)
        ['name', 'amount']

    """
    return [
        key1
        for key1, value1 in item1.items()
        for key2, value2 in item2.items()
        if key1 == key2 and value1 != value2
    ]


def asnumformat(dict:Dict, examples:Dict):
    return {
        key: number_format(value, examples.get(key))
        for key, value in dict.items()
    }


@reduce_kwargs('keymap')
def asmap(item:Dict, keymap:Dict):
    applied = {} 
    for key, value in item.items():
        app = keymap.get(key)
        if not app:
            applied[key] = value
            continue
        app = keymap[key]
        applied[key] = reduce_args_count(app, value, item)
    return applied


@reduce_kwargs('updatemap')
def asupdate(item:Dict, updatemap:Dict):
    """update item values

    :param item: a dict object
    :param updatemap: key:value|callable mapping for update values
    :return: updated item


    .. doctest::

        >>> item = {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'usa'}

        >>> # update by assign simple value directly
        >>> listorm.asupdate(item, age=100) 
        {'name': 'Smith', 'gender': 'M', 'age': 100, 'location': 'usa'}

        >>> # update value via function
        >>> listorm.asupdate(item, location=lambda location: str.upper(location))
        {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'}

        # as shortcut instead of using lambda
        >>> listorm.asupdate(item, location=str.upper)
        {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'}

    """
            
    updated = {}
    for key, value in item.items():
        app = updatemap.get(key)
        if not app:
            updated[key] = value
        else:
            updated.update(reduce_callback(item, key, app))        
    return updated
