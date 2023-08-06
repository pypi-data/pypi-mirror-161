import csv, xlrd, xlsxwriter
from io import TextIOBase, BufferedReader, StringIO, BytesIO


def to_io(path, *args, **kwargs):
    if isinstance(path, str):
        return open(path, *args, **kwargs)
    elif isinstance(path, (TextIOBase, BufferedReader)):
        return path
    else:
        raise ValueError('Either file path or fp must be specified')


def read_csv(file, encoding='utf-8'):
    fp = to_io(file, encoding=encoding)
    csv_reader = csv.reader(fp)
    fields = next(csv_reader)
    result = [dict(zip(fields, map(str, row))) for row in csv_reader]
    return result
    

def read_excel(file, sheet_index=0, starts_row=0):
    '''Excel File or byte Content of Excel to Listorm object
    '''
    fp = to_io(file, 'rb')
    content = fp.read()
    wb = xlrd.open_workbook(file_contents=content)
    ws = wb.sheet_by_index(sheet_index)
    fields = ws.row_values(starts_row)
    result = [dict(zip(fields, map(str, ws.row_values(r)))) for r in range(starts_row+1, ws.nrows)]
    return result
  


def write_csv(records:list[dict], filename=None):
    output = StringIO()
    writer = csv.DictWriter(output, lineterminator='\n')
    writer.writeheader()
    for row in records:
        writer.writerow(row)
    if filename:
        with open(filename, 'w') as fp:
            fp.write(output.getvalue())
    else:
        return output.getvalue()


def to_excel(records:list[dict], filename=None):
    '''If filnames is None, returns filecontents
    '''
    output = BytesIO()
    wb = xlsxwriter.Workbook(output)
    ws = wb.add_worksheet()

    for i, row in enumerate(records):
        if i == 0:
            values = [k for k in row]
        else:
            values = [v for k, v in row.items()]
        ws.write_row(i,0, values)
    wb.close()

    if filename:
        with open(filename, 'wb') as fp:
            fp.write(output.getvalue())
    else:
        return output.getvalue()