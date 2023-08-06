import os
from typing import List, Dict, Text, Tuple
from collections import abc


from .io import get_bytesio, reduce_excel_input
from ..records import fillmissed, values, askeys, select, merge
from ..row import asvalues
from ...utils import pluralize_params
from ...utils.excel import load_workbook, load_worksheet, open_workbook, save_workbook
from ...utils.plural import pluralize


def _find_table(values, fields_contains:List=None, start_rows:int=None, start_cols:int=None):
    def _find_start_row_by_fields(values, fields):
        fieldset = set(fields)
        for i, row in enumerate(values):
            if fieldset < set(row):
                return i
        raise ValueError("Cannot find start row number by {}".format(fields))

    def _find_column_offset(row):
        for i, col in enumerate(row):
            if not col:
                continue
            return i

    def _slice_padding(values, nrow, ncol):
        values = values[nrow:]
        return list(map(lambda row: row[ncol:], values))

    values = [val for val in values]
    if start_rows is None:
        start_rows = _find_start_row_by_fields(values, fields_contains)
    if start_cols is None:
        start_cols = _find_column_offset(values[start_rows])

    if start_rows == 0 and start_cols == 0:
        return values
    return _slice_padding(values, start_rows, start_cols)


def _normalize_columns(fields):
    results = []
    trantab = {
        '\n': '',
        '_x000D_': '',
        '_x000d_': '',
    }
    for col in fields:
        for t, c in trantab.items():
            col = col.replace(t, c)
        col = col.strip()
        results.append(col)
    return results


def read_excel(file=None, search_fields:List=None, sheet_name:Text=None, start_rows:int=0, start_cols:int=0, prettify_column_names:bool=True, read_only=True, close=True, **kwargs):
    '''Excel File or byte Content of Excel to Listorm object
    '''
    workbook = load_workbook(file, read_only=read_only, **kwargs)
    worksheet = load_worksheet(workbook, sheet_name, **kwargs)

    if search_fields:
        table = _find_table(worksheet.values, search_fields)
    else:
        table = _find_table(worksheet.values, start_rows=start_rows, start_cols=start_cols)

    if close:
        workbook.close()

    if table:
        fields, *records = table
    else:
        fields, records = [], []
    
    if prettify_column_names:
        fields = _normalize_columns(fields)
    return [
        dict(zip(fields, row)) for row in records
    ]


def write_excel(records:List[Dict], file=None, sheet_name:Text=None, fill_miss=True, write_only=True, close=True, **kwargs):
    if records := pluralize(records):
        if fill_miss:
            records = fillmissed(records)

        workbook = open_workbook(write_only=write_only, **kwargs)
        worksheet = load_worksheet(workbook, sheet_name, **kwargs)

        fields = askeys(records[0])
        selected = select(records, fields)
        rows = values(selected, flat_one=False)
        
        worksheet.append(fields)
        for row in rows:
            worksheet.append(row)
        return save_workbook(workbook, file, close=close, **kwargs)
    return b''

# @pluralize_params('uniques')
# def insert_excel(records:List[Dict], excel, uniques:Tuple[Text], mode=('create', 'update',), append=False, **kwargs):
#     if isinstance(excel, str):
#         if not os.path.exists(excel):
#             if 'create' in mode:
#                 return write_excel(records, excel, **kwargs)

#     rows = read_excel(excel, **kwargs)
#     merged = merge(rows, records, uniques, mode=mode, append=append)
#     return write_excel(merged, excel, **kwargs)



@pluralize_params('uniques')
def insert_excel(records:List[Dict], file=None, sheet_name:Text=None, uniques:Tuple=None, mode='create', append=True, **kwargs):
    if records:=pluralize(records):
        workbook = load_workbook(file, **kwargs)
        rows = read_excel(workbook, sheet_name=sheet_name, **kwargs)
        merged, count = merge(rows, records, uniques=uniques, mode=mode, append=append, with_count=True)
        write_excel(merged, file, sheet_name=sheet_name, **kwargs)
        return count
    return 0




    
