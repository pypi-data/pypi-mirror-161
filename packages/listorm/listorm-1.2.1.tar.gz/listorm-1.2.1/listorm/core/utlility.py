from ..api import extensions
from .orm import Listorm



def read_excel(file=None, fields_contains:list=None, uniques=None, sheet_name=None, start_rows=0, start_cols=0, prettify_column_names=True):
    '''import records from excel

    :param file: filename|fp, defaults to None
    :param fields_contains: a parts of column names to find excel table, defaults to None
    :param uniques: unique keys, defaults to None
    :param sheet_name: sheetname where records exists, defaults to None
    :param start_rows: cell rows where table starts, defaults to 0
    :param start_cols: cell col index where table starts, defaults to 0
    :param prettify_column_names: if True, remove seps linebreaker space..etc , defaults to True
    :return: Listorm object


    .. note::
        **fields_contains** : It finds a table that exists at any location in the Excel sheet through a part of the field name

    '''
    records = extensions.read_excel(
        file, fields_contains, sheet_name, start_rows, start_cols,
        prettify_column_names=prettify_column_names
    )
    return Listorm(
        records, fill_missed=False,
        uniques=uniques,
    )



def read_csv(file, encoding='utf-8', uniques=None, **csv_reader_kwargs):
    '''import records from csv file

    :param file: filename|fp
    :param encoding: encoding of csv text source, defaults to 'utf-8'
    :param uniques: columns to check unique, defaults to None
    :param csv_reader_kwargs: kwargs of csv.reader which builtin module csv
    :return: Listorm object
    '''

    records = extensions.read_csv(file, encoding=encoding, **csv_reader_kwargs)
    return Listorm(
        records, fill_missed=False,
        uniques=uniques
    )