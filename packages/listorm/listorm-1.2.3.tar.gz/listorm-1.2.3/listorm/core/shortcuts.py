from ..utils import reduce_kwargs, reduce_args, pluralize_params
from ..api import values_count, write_excel, write_csv, diff, set_number_format, merge



class ShortCutMixin:

    @property
    def exists(self):
        return len(self) != 0

    @property
    def first(self):
        if self:
            return self[0]
    
    @property
    def count(self):
        return len(self)

    @property
    def last(self):
        if self:
            return self[-1]

    def max(self, column:str):
        '''get maximum of column's values

        :param column: column name where get max
        :return: max of column values


        .. doctest::
        
            >>> userTable = [
            ...     {'name': 'Hong', 'gender': 'M', 'age': 18, 'location': 'Korea'},
            ...     {'name': 'Charse', 'gender': 'M', 'age': 19, 'location': 'USA'},
            ...     {'name': 'Lyn', 'gender': 'F', 'age': 28, 'location': 'China'},
            ...     {'name': 'Xiaomi', 'gender': 'M', 'age': 15, 'location': 'China'},
            ...     {'name': 'Park', 'gender': 'M', 'age': 29, 'location': 'Korea'},
            ...     {'name': 'Smith', 'gender': 'M', 'age': 17, 'location': 'USA'},
            ...     {'name': 'Lee', 'gender': 'F', 'age': 12, 'location': 'Korea'},
            ... ]

            >>> from listorm import Listorm
            >>> ls = Listorm(userTable)
            >>> ls.max('age')
            29
        '''
        values = filter(None, self.values(column))
        return max(values)

    def min(self, column:str):
        '''get minium of column's values

        :param column: column name where get min
        :return: min of column values


        .. doctest::

            >>> ls.min('age')
            12

        '''
        values = filter(None, self.values(column))
        return min(values)
    
    @reduce_kwargs('formats')
    def set_number_type(self, formats:dict):
        '''change number formats as default examples

        :param formats: number format examples
        :return: number formatted records


        .. doctest::

            >>> numbers = [
            ...     {
            ...       'flt': 0.5, 'string': '123', 'string_float': '123.5', 'int': 412, 'string_int': '5123', 'blabla': 'what?',  
            ...     }
            ... ]
            >>> lsnumber = Listorm(numbers)

            >>> # key name and example of types to change, if faild to change, example value will be default value
            >>> lsnumber.set_number_type(flt='', string=0.0, string_float=0, int='', string_int=0, blabla=0)
            [{'flt': '0.5', 'string': 123.0, 'string_float': 123, 'int': '412', 'string_int': 5123, 'blabla': 0}]

        '''
        records = set_number_format(self, formats=formats)
        return self.__class__(records)
        
    @reduce_args('columns')
    def values_count(self, columns:list):
        '''get values count by keys

        :param columns: column name for counting values
        :return: dict that has value occurance

        .. doctest::
        
            >>> lsb.values_count('product')
            {'battery': 2, 'keyboard': 2, 'cleaner': 2, 'monitor': 1, 'mouse': 3, 'hardcase': 1, 'keycover': 1, 'manual': 1, 'cable': 1, 'adopter': 1}

        '''
        return values_count(self, columns)
        
    def to_excel(self, filename=None, **kwargs):
        '''write to excel

        :param filename: output excel filename,  defaults to None
        :return: if filename is None, return file contents
        '''
        return write_excel(self, filename, fill_miss=False, **kwargs)


    def to_csv(self, filename=None, fields=None, encoding='utf-8', **csv_kwargs):
        '''write to csv

        :param filename: output csv filename, defaults to None
        :param fields: fields for retrieve, defaults to None
        :param encoding: encoding , defaults to 'utf-8'
        :return: if filename is None, return file contents
        '''
        return write_csv(self, filename, fields=fields, encoding=encoding, **csv_kwargs)

    def get_changes(self, other, pk=None):
        '''compare two records about added, deleted and updated on common columns

        :param other: another Listorm objects as records
        :param pk: unique keys for both of two records, defaults to None
        :return: namedtuple objects as Changes



        .. doctest::


            >>> before = [
            ...    {'name': 'Hong', 'gender': 'M', 'age': 18, 'location': 'Korea'},
            ...    {'name': 'Charse', 'gender': 'M', 'age': 19, 'location': 'USA'},
            ...    {'name': 'ohmyboss', 'gender': 'F', 'age': 17, 'location': 'USA'},
            ...    {'name': 'Lyn', 'gender': 'F', 'age': 29, 'location': 'China'},
            ... ]
            >>> after = [
            ...    {'name': 'Lyn', 'gender': 'F', 'age': 28, 'location': 'China'},
            ...    {'name': 'Xiaomi', 'gender': 'M', 'age': 15, 'location': 'China'},
            ...    {'name': 'ohmyboss', 'gender': 'M', 'age': 17, 'location': 'Canada'},
            ...    {'name': 'Park', 'gender': 'M', 'age': 29, 'location': 'Korea'},
            ... ]

            >>> ls_before = Listorm(before)
            >>> ls_after = Listorm(after)

            >>> changes = ls_before.get_changes(ls_after, pk='name')

            >>> changes.added
            [Added(pk='Xiaomi', rows={'name': 'Xiaomi', 'gender': 'M', 'age': 15, 'location': 'China'}), Added(pk='Park', rows={'name': 'Park', 'gender': 'M', 'age': 29, 'location': 'Korea'})]

            >>> changes.deleted
            [Deleted(pk='Hong', rows={'name': 'Hong', 'gender': 'M', 'age': 18, 'location': 'Korea'}), Deleted(pk='Charse', rows={'name': 'Charse', 'gender': 'M', 'age': 19, 'location': 'USA'})]

            >>> changes.updated
            [Updated(pk='ohmyboss', before={'name': 'ohmyboss', 'gender': 'F', 'age': 17, 'location': 'USA'}, after={'name': 'ohmyboss', 'gender': 'M', 'age': 17, 'location': 'Canada'}, where=['gender', 'location']), Updated(pk='Lyn', before={'name': 'Lyn', 'gender': 'F', 'age': 29, 'location': 'China'}, after={'name': 'Lyn', 'gender': 'F', 'age': 28, 'location': 'China'}, where=['age'])]

            >>> # usage of updated
            >>> for change in changes.updated:
            ...     print(change.pk)
            ...     for key in change.where:
            ...         print('where:', key)
            ...         print('  before->after:',change.before[key], '->', change.after[key])
            ...     print('------------------------------')
            ohmyboss
            where: gender
              before->after: F -> M
            where: location
              before->after: USA -> Canada
            ------------------------------
            Lyn
            where: age
              before->after: 29 -> 28
            ------------------------------

        '''
        if not pk and not all([self.uniques, other.uniques]):
            raise ValueError("Both of list has unique keys or specify pk for compare")
        elif not pk and self.uniques != other.uniques:
            raise ValueError("Both unique key fields({}, {}) must be same".format(self.uniques, other.uniques))
        elif not pk and not isinstance(other, self.__class__):
            raise ValueError("{} must be Listorm instance, not {}".format(other, type(other)))
        elif not all([self.exists, other.exists]):
            raise ValueError("Empty list not allowed:")
        
        diff_keys = pk or self.uniques or other.uniques
        return diff(self, other, diff_keys)


