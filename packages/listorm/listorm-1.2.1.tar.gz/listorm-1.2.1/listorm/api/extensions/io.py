from io import TextIOBase, BufferedReader, StringIO, BytesIO



def get_stringio(*args):
    return StringIO(*args)


def get_bytesio(*args):
    return BytesIO(*args)


def reduce_csv_input(file, **kwargs):
    if isinstance(file, str):
        with open(file, **kwargs) as fp:
            content = fp.read()
            return get_stringio(content)
    elif isinstance(file, TextIOBase):
        return file
    raise ValueError('Invalid csv file type')


def reduce_excel_input(file):
    if isinstance(file, str):
        with open(file, 'rb') as fp:
            return BytesIO(fp.read())
    elif isinstance(file, bytes):
        return BytesIO(file)
    elif isinstance(file, BufferedReader):
        return file
    else:
        raise ValueError('Invalid excel file type')

