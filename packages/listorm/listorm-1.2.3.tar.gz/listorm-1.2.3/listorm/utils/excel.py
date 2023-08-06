import os, io, pathlib
from typing import Text

import openpyxl

from .argtools import select_kwargs


def open_workbook(**kwargs):
    '''create new workbook'''
    return select_kwargs(openpyxl.Workbook, **kwargs)


def load_workbook(file=None, **kwargs):
    if isinstance(file, openpyxl.Workbook):
        return file
    if file is None:
        return open_workbook(**kwargs)
    if isinstance(file, (str, pathlib.PurePath)):
        if not os.path.exists(file):
            return open_workbook(**kwargs)
    return select_kwargs(openpyxl.load_workbook, file, **kwargs)


def load_worksheet(workbook:openpyxl.Workbook, sheet_name:Text=None, **kwargs):
    if sheet_name is None:
        if worksheet:= workbook.active:
            return worksheet
        sheet_name = 'Sheet1'
    if sheet_name in workbook.sheetnames:
        return workbook[sheet_name]

    return select_kwargs(workbook.create_sheet, sheet_name, **kwargs)


def save_workbook(workbook:openpyxl.Workbook, file=None, close=True):
    f = file or io.BytesIO()
    workbook.save(f)
    if close:
        workbook.close()
    if file is None and isinstance(f, io.BufferedIOBase):
        return f.getvalue()
    return file

    

