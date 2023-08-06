'''
Class Based API for records
--------------------------------
'''

from typing import List, Dict, Tuple, Callable, Text, Any, Union

from .base import BaseList
from .shortcuts import ShortCutMixin
from ..exceptions import *
from ..api import *
from ..utils import reduce_args, reduce_kwargs, pluralize_params



class Listorm(ShortCutMixin, BaseList):
    '''wrapper class for 

    :param records: list as records
    :param uniques: if specified, it check unique constraint, defaults to None
    :param fill_missed: if True fill missing values of rows, defaults to True
    :param fill_value: if specified, fill missing as specifed value, defaults to None

    '''

    def filter(self, where:callable):
        records = [
            row for row in self if reduce_where(row, where)
        ]
        return Listorm(
            records,
            uniques=self.uniques, fill_missed=False
        )


    @reduce_args('columns')
    def select(self, columns:List, *, excludes:List=None, where:Callable=None):
        '''Retrieves the item of the specified item

        :param columns: keys for selecting columns
        :param excludes: keys for excluding columns, defaults to None
        :param where: callback for filtering records, defaults to None
        :return: Listorm

        
        .. doctest::

            >>> from listorm import Listorm
            >>> userTable = [
            ...    {'name': 'Hong', 'gender': 'M', 'age': 18, 'location': 'Korea'},
            ...    {'name': 'Charse', 'gender': 'M', 'age': 19, 'location': 'USA'},
            ...    {'name': 'Lyn', 'gender': 'F', 'age': 28, 'location': 'China'},
            ...    {'name': 'Xiaomi', 'gender': 'M', 'age': 15, 'location': 'China'},
            ...    {'name': 'Park', 'gender': 'M', 'age': 29, 'location': 'Korea'},
            ...    {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'},
            ...    {'name': 'Lee', 'gender': 'F', 'age': 12, 'location': 'Korea'},
            ... ]

            ls = Listorm(userTable)
            ls.select('name', 'age', 'location', where=lambda age: age > 20).print()
            {'name': 'Lyn', 'age': 28, 'location': 'China'}
            {'name': 'Park', 'age': 29, 'location': 'Korea'}


        '''
        return Listorm(
            select(self, columns, excludes=excludes, where=where), 
            fill_missed=False
        )


    @reduce_args('columns')
    def drop_column(self, columns:List):
        '''delete columns


        .. doctest::

            >>> from listorm import Listorm

            >>> userTable = [
            ...    {'name': 'Hong', 'gender': 'M', 'age': 18, 'location': 'Korea'},
            ...    {'name': 'Charse', 'gender': 'M', 'age': 19, 'location': 'USA'},
            ...    {'name': 'Lyn', 'gender': 'F', 'age': 28, 'location': 'China'},
            ...    {'name': 'Xiaomi', 'gender': 'M', 'age': 15, 'location': 'China'},
            ...    {'name': 'Park', 'gender': 'M', 'age': 29, 'location': 'Korea'},
            ...    {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'},
            ...    {'name': 'Lee', 'gender': 'F', 'age': 12, 'location': 'Korea'},
            ... ]

            >>> ls = Listorm(userTable)
            >>> ls.drop_column('age', 'location').print()
            {'name': 'Hong', 'gender': 'M'}
            {'name': 'Charse', 'gender': 'M'}
            {'name': 'Lyn', 'gender': 'F'}
            {'name': 'Xiaomi', 'gender': 'M'}
            {'name': 'Park', 'gender': 'M'}
            {'name': 'Smith', 'gender': 'M'}
            {'name': 'Lee', 'gender': 'F'}


        :param columns: column name for delete
        :return: Listorm
        '''
        return self.select(excludes=columns)
    

    @reduce_kwargs('keymap')
    def add_column(self, keymap:Dict):
        '''extend row as new columns

        :param keymap: new column: function mapping
        :return: Listorm

        
        .. doctest::

            >>> from listorm import Listorm

            >>> userTable = [
            ...    {'name': 'Hong', 'gender': 'M', 'age': 18, 'location': 'Korea'},
            ...    {'name': 'Charse', 'gender': 'M', 'age': 19, 'location': 'USA'},
            ...    {'name': 'Lyn', 'gender': 'F', 'age': 28, 'location': 'China'},
            ...    {'name': 'Xiaomi', 'gender': 'M', 'age': 15, 'location': 'China'},
            ...    {'name': 'Park', 'gender': 'M', 'age': 29, 'location': 'Korea'},
            ...    {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'},
            ...    {'name': 'Lee', 'gender': 'F', 'age': 12, 'location': 'Korea'},
            ... ]

            >>> ls = Listorm(userTable)

            >>> ls.add_column(
            ...    summary=lambda name, gender, age: f"{name}/{gender}/{age}"
            ... ).print()
            {'name': 'Hong', 'gender': 'M', 'age': 18, 'location': 'Korea', 'summary': 'Hong/M/18'}
            {'name': 'Charse', 'gender': 'M', 'age': 19, 'location': 'USA', 'summary': 'Charse/M/19'}
            {'name': 'Lyn', 'gender': 'F', 'age': 28, 'location': 'China', 'summary': 'Lyn/F/28'}
            {'name': 'Xiaomi', 'gender': 'M', 'age': 15, 'location': 'China', 'summary': 'Xiaomi/M/15'}
            {'name': 'Park', 'gender': 'M', 'age': 29, 'location': 'Korea', 'summary': 'Park/M/29'}
            {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA', 'summary': 'Smith/M/17'}
            {'name': 'Lee', 'gender': 'F', 'age': 12, 'location': 'Korea', 'summary': 'Lee/F/12'}

        '''
        return Listorm(
            add_column(self, keymap=keymap),
            **self.as_kwargs(fill_missed=False)
        )


    @reduce_kwargs('renamemap')
    def rename(self, renamemap:Dict):
        '''change columns name

        :param renamemap: old:new mapping of column names
        :return: Listorm

        .. doctest::


            >>> from listorm import Listorm
            >>> ls = Listorm(userTable)

            >>> ls.rename(gender='sex', location='country').print()
            {'name': 'Hong', 'sex': 'M', 'age': 18, 'country': 'Korea'}
            {'name': 'Charse', 'sex': 'M', 'age': 19, 'country': 'USA'}
            {'name': 'Lyn', 'sex': 'F', 'age': 28, 'country': 'China'}
            {'name': 'Xiaomi', 'sex': 'M', 'age': 15, 'country': 'China'}
            {'name': 'Park', 'sex': 'M', 'age': 29, 'country': 'Korea'}
            {'name': 'Smith', 'sex': 'M', 'age': 17, 'country': 'USA'}
            {'name': 'Lee', 'sex': 'F', 'age': 12, 'country': 'Korea'}

            >>> # if key name has to be containing spaces
            >>> ls.rename(renamemap={'age': 'age of ultron' }).print()
            {'name': 'Hong', 'gender': 'M', 'age of ultron': 18, 'location': 'Korea'}
            {'name': 'Charse', 'gender': 'M', 'age of ultron': 19, 'location': 'USA'}
            {'name': 'Lyn', 'gender': 'F', 'age of ultron': 28, 'location': 'China'}
            {'name': 'Xiaomi', 'gender': 'M', 'age of ultron': 15, 'location': 'China'}
            {'name': 'Park', 'gender': 'M', 'age of ultron': 29, 'location': 'Korea'}
            {'name': 'Smith', 'gender': 'M', 'age of ultron': 17, 'location': 'USA'}
            {'name': 'Lee', 'gender': 'F', 'age of ultron': 12, 'location': 'Korea'}

        '''
        return Listorm(rename(self, renamemap=renamemap), fill_missed=False)


    @reduce_kwargs('updatemap')
    def update(self, updatemap:Dict, *, where:callable=None):
        '''update row values

        :param updatemap: column: value|function map for update values
        :param where: specifying what to update, defaults to None
        :return: Listorm


        .. doctest::

            >>> ls.update(
            ...    age=lambda age: age + 1,
            ...    where=lambda location: location.lower() in ['korea', 'china']
            ... ).print()
            {'name': 'Hong', 'gender': 'M', 'age': 19, 'location': 'Korea'}
            {'name': 'Charse', 'gender': 'M', 'age': 19, 'location': 'USA'}
            {'name': 'Lyn', 'gender': 'F', 'age': 29, 'location': 'China'}
            {'name': 'Xiaomi', 'gender': 'M', 'age': 16, 'location': 'China'}
            {'name': 'Park', 'gender': 'M', 'age': 30, 'location': 'Korea'}
            {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'}
            {'name': 'Lee', 'gender': 'F', 'age': 13, 'location': 'Korea'}

        '''
        return Listorm(
            update(self, updatemap=updatemap, where=where),
            fill_missed=False
        )
    

    @reduce_args('columns')
    def values(self, columns:List, *, flat_one=True):
        '''extract values from row

        :param columns: column names to extract values
        :param flat_one: If True, when the return value is a single value, the value is returned without being included in the list, defaults to True, defaults to True
        :return: list


        .. doctest::

            >>> values = ls.values('name', 'gender', 'location')
            >>> for v in values: print(v)
            ('Hong', 'M', 'Korea')
            ('Charse', 'M', 'USA')
            ('Lyn', 'F', 'China')
            ('Xiaomi', 'M', 'China')
            ('Park', 'M', 'Korea')
            ('Smith', 'M', 'USA')
            ('Lee', 'F', 'Korea')

            >>> # When there is only one column, a flatten single list is returned
            >>> ls.values('name')
            ['Hong', 'Charse', 'Lyn', 'Xiaomi', 'Park', 'Smith', 'Lee']

            >>> # but, flat_one = False when consistency is required
            >>> ls.values('name', flat_one=False)
            [('Hong',), ('Charse',), ('Lyn',), ('Xiaomi',), ('Park',), ('Smith',), ('Lee',)]

        '''
        return values(self, columns, flat_one=flat_one)


    @reduce_args('columns')
    def distinct(self, columns:List, *, keep_first:bool=True, singles:bool=False):
        '''remove duplicated rows by columns

        :param columns: column names for check duplicated values
        :param keep_first: If True, in case of duplicate occurrence select the first item that appears, else last, defaults to True
        :param singles: If True, eliminate rows that have been duplicated. That is, only items that were unique are left. defaults to False, defaults to False
        :return: Listorm


        .. doctest::

            >>> buyTable = [
            ...     {'name': 'Xiaomi', 'product': 'battery', 'amount':7},
            ...     {'name': 'Hong', 'product': 'keyboard', 'amount':1},
            ...     {'name': 'Lyn', 'product': 'cleaner', 'amount':5},
            ...     {'name': 'Hong', 'product': 'monitor', 'amount':1},
            ...     {'name': 'Hong', 'product': 'mouse', 'amount':3},
            ...     {'name': 'Lyn', 'product': 'mouse', 'amount':1},
            ...     {'name': 'Unknown', 'product': 'keyboard', 'amount':1},
            ...     {'name': 'Lee', 'product': 'hardcase', 'amount':2},
            ...     {'name': 'Lee', 'product': 'keycover', 'amount':2},
            ...     {'name': 'Yuki', 'product': 'manual', 'amount':1},
            ...     {'name': 'Xiaomi', 'product': 'cable', 'amount':1},
            ...     {'name': 'anonymous', 'product': 'adopter', 'amount':2},
            ...     {'name': 'Park', 'product': 'battery', 'amount':2},
            ...     {'name': 'Hong', 'product': 'cleaner', 'amount':3},
            ...     {'name': 'Smith', 'product': 'mouse', 'amount':1},
            ... ]

            >>> len(buyTable)
            15

            >>> lsb = Listorm(buyTable)

            >>> lsb.distinct('name', 'amount').count
            12

            >>> lsb.distinct('name').print()
            {'name': 'Xiaomi', 'product': 'battery', 'amount': 7}
            {'name': 'Hong', 'product': 'keyboard', 'amount': 1}
            {'name': 'Lyn', 'product': 'cleaner', 'amount': 5}
            {'name': 'Unknown', 'product': 'keyboard', 'amount': 1}
            {'name': 'Lee', 'product': 'hardcase', 'amount': 2}
            {'name': 'Yuki', 'product': 'manual', 'amount': 1}
            {'name': 'anonymous', 'product': 'adopter', 'amount': 2}
            {'name': 'Park', 'product': 'battery', 'amount': 2}
            {'name': 'Smith', 'product': 'mouse', 'amount': 1}


            # distinct by unique together by name, amount
            >>> lsb.distinct('name', 'amount').print()
            {'name': 'Xiaomi', 'product': 'battery', 'amount': 7}
            {'name': 'Hong', 'product': 'keyboard', 'amount': 1}
            {'name': 'Lyn', 'product': 'cleaner', 'amount': 5}
            {'name': 'Hong', 'product': 'mouse', 'amount': 3}
            {'name': 'Lyn', 'product': 'mouse', 'amount': 1}
            {'name': 'Unknown', 'product': 'keyboard', 'amount': 1}
            {'name': 'Lee', 'product': 'hardcase', 'amount': 2}
            {'name': 'Yuki', 'product': 'manual', 'amount': 1}
            {'name': 'Xiaomi', 'product': 'cable', 'amount': 1}
            {'name': 'anonymous', 'product': 'adopter', 'amount': 2}
            {'name': 'Park', 'product': 'battery', 'amount': 2}
            {'name': 'Smith', 'product': 'mouse', 'amount': 1}

            >>> # if singles is True, retrive the item only the name exist once
            >>> lsb.distinct('name', singles=True).print()
            {'name': 'Unknown', 'product': 'keyboard', 'amount': 1}
            {'name': 'Yuki', 'product': 'manual', 'amount': 1}
            {'name': 'anonymous', 'product': 'adopter', 'amount': 2}
            {'name': 'Park', 'product': 'battery', 'amount': 2}
            {'name': 'Smith', 'product': 'mouse', 'amount': 1}

        '''
        return Listorm(distinct(self, columns, keep_first=keep_first, singles=singles), fill_missed=False)


    @reduce_args('sortkeys')
    def orderby(self, sortkeys:List):
        '''sort rows 

        :param sortkeys: column names or function for make sort keys
        :return: Listorm

        .. doctest::

            >>> # complex key sorting: location as ascending and by age decending
            >>> ls.orderby(userTable, 'location', '-age').print()
            {'name': 'Lyn', 'gender': 'F', 'age': 28, 'location': 'China'}
            {'name': 'Xiaomi', 'gender': 'M', 'age': 15, 'location': 'China'}
            {'name': 'Park', 'gender': 'M', 'age': 29, 'location': 'Korea'}
            {'name': 'Hong', 'gender': 'M', 'age': 18, 'location': 'Korea'}
            {'name': 'Lee', 'gender': 'F', 'age': 12, 'location': 'Korea'}
            {'name': 'Charse', 'gender': 'M', 'age': 19, 'location': 'USA'}
            {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'}

            >>> # ordering by callback
            >>> # order by first digit of age
            >>> ls.orderby(userTable, lambda age: str(age)[-1]).print()
            {'name': 'Lee', 'gender': 'F', 'age': 12, 'location': 'Korea'}
            {'name': 'Xiaomi', 'gender': 'M', 'age': 15, 'location': 'China'}
            {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'}
            {'name': 'Hong', 'gender': 'M', 'age': 18, 'location': 'Korea'}
            {'name': 'Lyn', 'gender': 'F', 'age': 28, 'location': 'China'}
            {'name': 'Charse', 'gender': 'M', 'age': 19, 'location': 'USA'}
            {'name': 'Park', 'gender': 'M', 'age': 29, 'location': 'Korea'}

        .. note::

            If you are familiar with django it looks like it

        '''
        return Listorm(orderby(self, sortkeys), **self.as_kwargs(fill_missed=False))


    @reduce_args('columns')
    @reduce_kwargs('aggset')
    def groupby(self, columns:List, *, aggset:Dict, renames:Dict=None, groupset_name:Text=None):
        '''grouping rows and aggregate valeus

        :param columns: column names for grouping
        :param aggset: aggregate column: function map
        :param renames: the name of aggregated columns, if None, as original column name, default None
        :param groupset_name: if specified, grouped items are dangling, default None
        :return: Listorm


        .. doctest::

            >>> # get gender numbers by location
            >>> ls.groupby(
            ...     'location', 'gender', #1. grouping
            ...      gender=len,  #2 caclulating
            ...      renames={'gender': 'gender_count'} #3 retriving as other keyname
            ... ).print()
            {'location': 'Korea', 'gender': 'M', 'gender_count': 2}
            {'location': 'USA', 'gender': 'M', 'gender_count': 2}
            {'location': 'China', 'gender': 'F', 'gender_count': 1}
            {'location': 'China', 'gender': 'M', 'gender_count': 1}
            {'location': 'Korea', 'gender': 'F', 'gender_count': 1}

            >>> # get average of age by gender
            >>> def calc_average_age(values):
            ...     return sum(values) / len(values)

            >>> ls.groupby(
            ...   'gender',
            ...   age=calc_average_age,
            ...   renames={'age': 'age_avg'}
            ... )
            [{'gender': 'M', 'age_avg': 19.6}, {'gender': 'F', 'age_avg': 20.0}]


            .. note::
                
                Although groupby's parameterizing is rather complicated, tt is largely divided into three parts.
                * keys
                * aggregation
                * renaming for retrieve aggregation


        '''
        return Listorm(
            groupby(self, columns, aggset=aggset, renames=renames, groupset_name=groupset_name)
        )


    @pluralize_params('left_on', 'right_on')
    def join(self, other, left_on:Union[Text, Tuple]=None, right_on:Union[Text, Tuple]=None, how:Text='inner'):
        '''merge other records

        :param other: another Listorm object
        :param left_on: columns for join on left side records
        :param right_on: columns for join on right side records
        :param how: how to join 'inner', 'left', 'right', 'outer', defaults to 'inner'
        :return: Listorm


        '''
        left_on = left_on or self.uniques        
        
        if not right_on:
            if isinstance(other, Listorm):
                right_on = other.uniques or left_on
            else:
                right_on = left_on
        if not all((left_on, right_on)):
            raise JoinKeyDoesNotExists('on:{}, right_on:{} must be specified'.format(left_on, right_on))
        return Listorm(
                join(self, other, None, left_on, right_on, how=how),
                fill_value=self.fill_value
            )

    
    @pluralize_params('pk', 'mode')
    def merge(self, other, pk=None, mode=('create', 'update'), append=False, **kwargs):
        '''Update information of self to other based on pk
           If mode is create, it merges other that do not have duplicate pk
           If mode is update, then other is overwritten with self

        :param other: records to update
        :param pk: common unique keys
        :param mode: the set of methods- create, update, delete defaults to ('create', 'update')
        :param append: Determind insert a new row at the beginning or at the end , defaults to False
        :return: Listorm
        '''

        pk = pk or self.uniques or other.uniques

        if not pk:
            raise ValueError('pk must be specified or pre setted as uniques of Listorm')

        merged = merge(self, other, pk, mode=mode, append=append)
        return Listorm(merged, **self.as_kwargs(fill_missed=False))