import csv
from typing import List, Dict


from ..records import get_allkeys
from .io import get_stringio, reduce_csv_input



def read_csv(file, encoding='utf-8', fields:List=None, **csv_kwargs):
    fp = reduce_csv_input(file, encoding=encoding)
    csv_reader = csv.reader(fp, **csv_kwargs)
    fields = fields or next(csv_reader)
    result = [dict(zip(fields, map(str, row))) for row in csv_reader]
    return result



def write_csv(records:List[Dict], filename=None, fields=None, encoding='utf-8', **csv_kwargs):
    csv_kwargs.update({'lineterminator':'\n'})
    output = get_stringio()
    fields = fields or get_allkeys(records)
    writer = csv.DictWriter(output, fields, **csv_kwargs)
    writer.writeheader()
    for row in records:
        writer.writerow(row)
    if filename:
        with open(filename, 'w', encoding=encoding) as fp:
            fp.write(output.getvalue())
    else:
        return output.getvalue()
