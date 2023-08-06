'''
test doc string
'''


class UniqueConstraintError(Exception):
    '''Unique constratint failed'''
    pass

class JoinKeyDoesNotExists(Exception):
    '''join key does not exists'''
    pass

class ApplyFunctionArgumentCountError(Exception):

    def __str__(self):
        func, *_ = self.args
        msg = "Arguments count for applying function({}) must be 1 or 2".format(func.__name__)
        return msg
